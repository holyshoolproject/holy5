
# student/management/commands/import_fee_rec.py
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from decimal import Decimal, InvalidOperation
import re
import pandas as pd

# ---- Adjust these imports to match your project layout ----
# Replace `app_name` with the Django app that contains these models.
from fees.models import StudentFeeRecord, FeeStructure, AcademicYear, GradeClass  # <-- CHANGE app_name
from student.models import Term, StudentProfile  # Update if StudentProfile/Term live elsewhere


class Command(BaseCommand):
    help = (
        "Import StudentFeeRecord rows from Excel/CSV using combined 'Fee Structure' and 'Student Name'. "
        "Format example: Fee Structure = 'class 1 - 1st Term - (2025/2026) — 350.00 GHS'; "
        "Student Name = 'Jason Asare - Asiedu - nursery 2' (name + trailing class)."
    )

    def add_arguments(self, parser):
        parser.add_argument("--file", required=True, help="Path to Excel (.xlsx) or CSV file.")
        parser.add_argument("--sheet", default=None, help="Excel sheet name (if .xlsx). Defaults to first sheet.")
        parser.add_argument("--dry-run", action="store_true", help="Validate without writing changes.")
        parser.add_argument("--upsert", action="store_true",
                            help="Update existing records matching --match-fields key.")
        parser.add_argument("--match-fields", nargs="*",
                            default=["student", "fee_structure"],
                            help="Fields to match when --upsert is set. Choose any of: student, fee_structure.")
        parser.add_argument("--debug", action="store_true", help="Print detected columns and parsing steps.")
        # Default behavior is to IGNORE student IDs even if present
        parser.add_argument("--use-student-id", action="store_true",
                            help="(Optional) Use 'Student ID' to resolve students. Default: OFF.")

    # ----------------- Utility coercers -----------------

    @staticmethod
    def _coerce_decimal(val, field_label):
        try:
            return Decimal(str(val)).quantize(Decimal("0.01"))
        except (InvalidOperation, TypeError):
            raise ValueError(f"Invalid {field_label}: {val}")

    @staticmethod
    def _coerce_bool(val, field_label):
        if pd.isna(val):
            return False
        s = str(val).strip().lower()
        if s in {"true", "yes", "y", "1"}:
            return True
        if s in {"false", "no", "n", "0"}:
            return False
        if isinstance(val, bool):
            return val
        try:
            return bool(int(Decimal(str(val))))
        except Exception:
            raise ValueError(f"Invalid {field_label}: {val}")

    @staticmethod
    def _find_col(df, target_names):
        """Find a column whose name matches any of target_names (case-insensitive)."""
        targets_lower = {t.strip().lower() for t in target_names}
        for c in df.columns:
            if str(c).strip().lower() in targets_lower:
                return c
        return None

    # ----------------- Parsers for your sheet format -----------------

    def _parse_student_name(self, raw, grade_class_name=None):
        """
        Examples:
          - 'kelvin Nyarko - class 1'            -> 'kelvin Nyarko'
          - 'Jason Asare - Asiedu - nursery 2'   -> 'Jason Asare - Asiedu'
          - 'Mary-Jane Agyeman'                  -> 'Mary-Jane Agyeman' (unchanged)

        We split on ' - ' but only remove the trailing part if it matches the
        grade_class_name (case-insensitive). Internal hyphens in names are preserved.
        """
        if raw is None or pd.isna(raw):
            return None

        s = str(raw).strip()
        parts = [p.strip() for p in re.split(r"\s+-\s+", s)]

        if not parts:
            return s

        if grade_class_name:
            last_seg = parts[-1].strip().lower()
            cls_norm = str(grade_class_name).strip().lower()
            if last_seg == cls_norm and len(parts) >= 2:
                return " - ".join(parts[:-1]).strip()

        return s  # leave unchanged if we can't confidently identify the trailing class

    def _parse_fee_structure_cell(self, raw):
        """
        Parse strings like:
          'class 1 - 1st Term - (2025/2026) — 350.00 GHS'
        into (grade_class_name, term_name, academic_year_name, amount_decimal).

        Supports either '—' (em dash) or '-' as the amount separator, and optional currency suffix.
        """
        if raw is None or pd.isna(raw):
            raise ValueError("Fee Structure cell is empty.")

        text = str(raw).strip()

        # Split left side and amount by em dash if present
        if "—" in text:
            left, amount_part = [t.strip() for t in text.split("—", 1)]
        else:
            left, amount_part = text, ""

        # Extract triplet: grade_class - term - (AY)
        left_parts = [p.strip() for p in left.split(" - ")]
        if len(left_parts) < 3:
            raise ValueError(f"Fee Structure format not recognized: '{text}'")

        grade_class_name = left_parts[0]
        term_name = left_parts[1]

        # AY enclosed in parentheses, e.g., (2025/2026)
        m_ay = re.search(r"\(([^)]+)\)", left_parts[2])
        if not m_ay:
            raise ValueError(f"Academic Year not found in Fee Structure: '{text}'")
        academic_year_name = m_ay.group(1).strip()

        # Amount: try to find numeric part
        amount_str = None
        if amount_part:
            m_amt = re.search(r"([0-9]+(?:\.[0-9]{1,2})?)", amount_part)
            if m_amt:
                amount_str = m_amt.group(1)
        if amount_str is None:
            m_amt2 = re.search(r"\)\s*[—-]\s*([0-9]+(?:\.[0-9]{1,2})?)", text)
            if m_amt2:
                amount_str = m_amt2.group(1)

        fee_amount = self._coerce_decimal(amount_str, "FeeStructure Amount") if amount_str else None

        return grade_class_name, term_name, academic_year_name, fee_amount

    # ----------------- FK resolvers -----------------

    def _resolve_student_by_name(self, full_name, grade_class_name=None):
        """
        Resolve StudentProfile by user.full_name (case-insensitive).
        If multiple matches, and StudentProfile has a grade_class FK, further filter by grade_class name.
        """
        if not full_name:
            raise ValueError("Student Name is empty.")

        qs = StudentProfile.objects.filter(user__full_name__iexact=full_name)

        count = qs.count()
        if count == 0:
            raise ValueError(f"StudentProfile with user.full_name '{full_name}' not found.")
        if count == 1:
            return qs.first()

        # Disambiguate by class if model has that relation
        if grade_class_name and hasattr(StudentProfile, "grade_class"):
            qs2 = qs.filter(grade_class__name__iexact=grade_class_name)
            if qs2.count() == 1:
                return qs2.first()

        # Still ambiguous
        raise ValueError(
            f"Multiple StudentProfiles found for '{full_name}'. "
            f"Add a unique identifier or enable --use-student-id for disambiguation."
        )

    def _resolve_fee_structure_by_triplet(self, grade_class_name, term_name, academic_year_name):
        # AcademicYear
        try:
            ay = AcademicYear.objects.get(name__iexact=academic_year_name)
        except AcademicYear.DoesNotExist:
            raise ValueError(f"AcademicYear with name '{academic_year_name}' not found.")

        # GradeClass
        try:
            gc = GradeClass.objects.get(name__iexact=grade_class_name)
        except GradeClass.DoesNotExist:
            raise ValueError(f"GradeClass with name '{grade_class_name}' not found.")

        # Term (and validate AY)
        try:
            tm = Term.objects.get(name__iexact=term_name)
        except Term.DoesNotExist:
            raise ValueError(f"Term with name '{term_name}' not found.")
        if getattr(tm, "academic_year_id", None) and tm.academic_year_id != ay.id:
            raise ValueError(
                f"Term '{tm.name}' belongs to AcademicYear ID {tm.academic_year_id}, "
                f"but row specifies AcademicYear '{ay.name}'."
            )

        # FeeStructure
        try:
            fs = FeeStructure.objects.select_related("academic_year", "grade_class", "term") \
                                     .get(academic_year=ay, grade_class=gc, term=tm)
        except FeeStructure.DoesNotExist:
            raise ValueError(f"FeeStructure not found for AY '{ay.name}', Class '{gc.name}', Term '{tm.name}'.")

        return fs, Decimal(fs.amount).quantize(Decimal("0.01"))

    # ----------------- Command handler -----------------

    def handle(self, *args, **options):
        infile = options["file"]
        sheet = options["sheet"]
        dry_run = options["dry_run"]
        upsert = options["upsert"]
        match_fields = options["match_fields"]
        debug = options.get("debug", False)
        use_student_id = options.get("use_student_id", False)

        # --- Load file (Excel or CSV) ---
        try:
            if infile.lower().endswith(".xlsx"):
                if sheet:
                    df = pd.read_excel(infile, sheet_name=sheet, engine="openpyxl")
                else:
                    df = pd.read_excel(infile, sheet_name=0, engine="openpyxl")
            elif infile.lower().endswith(".csv"):
                df = pd.read_csv(infile)
            else:
                raise CommandError("Unsupported file type. Use .xlsx or .csv")
        except Exception as e:
            raise CommandError(f"Failed to read file '{infile}': {e}")

        if isinstance(df, dict):
            first_key = next(iter(df))
            df = df[first_key]
        if not isinstance(df, pd.DataFrame):
            raise CommandError("Loaded object is not a DataFrame. Check your --sheet argument and file content.")

        # Normalize headers
        df.columns = [str(c).strip() for c in df.columns]
        if debug:
            self.stdout.write(self.style.WARNING("Detected columns:"))
            for c in df.columns:
                self.stdout.write(f"  - {c}")

        # Columns in your sheet
        student_id_col    = self._find_col(df, ["Student ID"])      # ignored unless --use-student-id
        student_name_col  = self._find_col(df, ["Student Name"])
        fee_structure_col = self._find_col(df, ["Fee Structure"])
        amount_paid_col   = self._find_col(df, ["Amount Paid"])
        balance_col       = self._find_col(df, ["Balance"])
        is_fully_paid_col = self._find_col(df, ["Is Fully Paid", "Fully Paid", "Paid?"])
        date_created_col  = self._find_col(df, ["Date Created"])

        # Validate presence
        if not student_name_col and not (use_student_id and student_id_col):
            raise CommandError("Missing student identifier: 'Student Name' is required (IDs ignored by default).")
        if not fee_structure_col:
            raise CommandError("Missing 'Fee Structure' column (combined: Class - Term - (AY) — Amount).")
        if not amount_paid_col:
            raise CommandError("Missing 'Amount Paid' column.")

        # Pre-fetch existing for upsert
        existing_map = {}
        if upsert:
            valid_fields = {"student", "fee_structure"}
            if not set(match_fields).issubset(valid_fields):
                raise CommandError(f"--match-fields must be subset of {valid_fields}")
            qs = StudentFeeRecord.objects.select_related("student", "fee_structure")
            for sfr in qs:
                key = tuple(getattr(sfr, f"{f}_id") for f in match_fields)
                existing_map[key] = sfr

        to_create, to_update, errors = [], [], []

        # Iterate rows
        for idx, row in df.iterrows():
            row_no = idx + 2  # account for header

            # Parse Fee Structure cell → resolve FS in DB
            try:
                gc_name, tm_name, ay_name, fs_amount_cell = self._parse_fee_structure_cell(row.get(fee_structure_col))
                fee_structure, fs_amount_db = self._resolve_fee_structure_by_triplet(gc_name, tm_name, ay_name)
                if fs_amount_cell is not None and fs_amount_cell != fs_amount_db:
                    errors.append((row_no, f"FeeStructure amount mismatch: file {fs_amount_cell} vs DB {fs_amount_db}"))
                    continue
            except ValueError as e:
                errors.append((row_no, str(e)))
                continue

            # Resolve student — IGNORE IDs unless explicitly allowed
            try:
                if use_student_id and student_id_col and pd.notna(row.get(student_id_col)):
                    stu_id = int(Decimal(str(row.get(student_id_col))))
                    student = StudentProfile.objects.get(id=stu_id)
                else:
                    full_name = self._parse_student_name(row.get(student_name_col), grade_class_name=gc_name)
                    if debug:
                        self.stdout.write(f"Row {row_no}: parsed student name -> '{full_name}' (class='{gc_name}')")
                    student = self._resolve_student_by_name(full_name, grade_class_name=gc_name)
            except Exception as e:
                errors.append((row_no, str(e)))
                continue

            # Amounts
            try:
                amount_paid = self._coerce_decimal(row.get(amount_paid_col), "Amount Paid")
            except ValueError as e:
                errors.append((row_no, str(e)))
                continue

            # Balance: optional; if missing, compute
            if balance_col and pd.notna(row.get(balance_col)):
                try:
                    balance = self._coerce_decimal(row.get(balance_col), "Balance")
                except ValueError as e:
                    errors.append((row_no, str(e)))
                    continue
            else:
                balance = (fs_amount_db - amount_paid).quantize(Decimal("0.01"))

            # Fully paid: optional; if missing, deduce
            if is_fully_paid_col and pd.notna(row.get(is_fully_paid_col)):
                try:
                    is_fully_paid = self._coerce_bool(row.get(is_fully_paid_col), "Is Fully Paid")
                except ValueError as e:
                    errors.append((row_no, str(e)))
                    continue
            else:
                is_fully_paid = (balance == Decimal("0.00"))

            # Consistency checks
            if (amount_paid + balance) != fs_amount_db:
                errors.append((row_no, f"Amount Paid + Balance ({amount_paid + balance}) != FeeStructure amount ({fs_amount_db})"))
                continue
            if is_fully_paid and balance != Decimal("0.00"):
                errors.append((row_no, f"is_fully_paid is True but balance = {balance}"))
                continue

            # Date created (optional)
            date_created_val = row.get(date_created_col) if date_created_col else None

            # Create/upsert
            if upsert:
                key = tuple(getattr(x, "id") for x in (student, fee_structure))  # (student_id, fee_structure_id)
                existing = existing_map.get(key)
                if existing:
                    existing.amount_paid = amount_paid
                    existing.balance = balance
                    existing.is_fully_paid = is_fully_paid
                    if date_created_val:
                        try:
                            existing.date_created = pd.to_datetime(date_created_val)
                        except Exception:
                            pass
                    to_update.append(existing)
                else:
                    sfr = StudentFeeRecord(
                        student=student, fee_structure=fee_structure,
                        amount_paid=amount_paid, balance=balance, is_fully_paid=is_fully_paid
                    )
                    if date_created_val:
                        try:
                            sfr.date_created = pd.to_datetime(date_created_val)
                        except Exception:
                            pass
                    to_create.append(sfr)
            else:
                sfr = StudentFeeRecord(
                    student=student, fee_structure=fee_structure,
                    amount_paid=amount_paid, balance=balance, is_fully_paid=is_fully_paid
                )
                if date_created_val:
                    try:
                        sfr.date_created = pd.to_datetime(date_created_val)
                    except Exception:
                        pass
                to_create.append(sfr)

        # Report
        if errors:
            self.stdout.write(self.style.WARNING("Validation errors:"))
            for row_no, msg in errors:
                self.stdout.write(f"  Row {row_no}: {msg}")

        self.stdout.write(
            f"Prepared: {len(to_create)} create(s), {len(to_update)} update(s). "
            f"Errors: {len(errors)}."
        )

        if dry_run:
            self.stdout.write(self.style.WARNING("Dry-run mode: no changes were written."))
            return

        if errors:
            raise CommandError("Aborting due to validation errors. Fix the file and re-run.")

        # Commit
        with transaction.atomic():
            if to_create:
                StudentFeeRecord.objects.bulk_create(to_create, batch_size=500)
            for sfr in to_update:
                sfr.save(update_fields=["amount_paid", "balance", "is_fully_paid", "date_created"])

        self.stdout.write(self.style.SUCCESS(
            f"Import complete: created {len(to_create)}, updated {len(to_update)}."
        ))
