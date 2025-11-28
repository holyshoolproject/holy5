
# student/management/commands/import_fee_structures.py
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from decimal import Decimal, InvalidOperation

import pandas as pd

# Adjust these imports to match your project layout
from fees.models import FeeStructure, AcademicYear, GradeClass  # <-- change app_name to your actual app
from student.models import Term  # if Term is in a different app, update this import


class Command(BaseCommand):
    help = "Import FeeStructure rows from an Excel (.xlsx) or CSV file."

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            required=True,
            help="Path to Excel (.xlsx) or CSV file."
        )
        parser.add_argument(
            "--sheet",
            default=None,
            help="Excel sheet name (if .xlsx). Defaults to first sheet."
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Validate and show changes without writing to the DB."
        )
        parser.add_argument(
            "--upsert",
            action="store_true",
            help="Update existing records matching (academic_year, grade_class, term) or given --match-fields."
        )
        parser.add_argument(
            "--match-fields",
            nargs="*",
            default=["academic_year", "grade_class", "term"],
            help="Fields to match when --upsert is set. Choose from: academic_year, grade_class, term."
        )

    # ----------------- Helpers -----------------

    @staticmethod
    def _find_col(df, target_names):
        """
        Find a column in df whose name matches any of target_names (case-insensitive).
        Returns the actual column name or None.
        """
        targets_lower = {t.strip().lower() for t in target_names}
        for c in df.columns:
            if str(c).strip().lower() in targets_lower:
                return c
        return None

    @staticmethod
    def _coerce_int(val, field_label):
        """Robustly coerce numeric-like values to int."""
        if pd.isna(val):
            raise ValueError(f"{field_label} is empty.")
        try:
            # Handles 2, "2", 2.0, "2.0"
            return int(Decimal(str(val)))
        except Exception:
            raise ValueError(f"Invalid {field_label}: {val}")

    @staticmethod
    def _coerce_decimal(val, field_label="Amount"):
        """Coerce value to Decimal with 2 dp."""
        try:
            return Decimal(str(val)).quantize(Decimal("0.01"))
        except (InvalidOperation, TypeError):
            raise ValueError(f"Invalid {field_label}: {val}")

    # ----------------- Command handler -----------------

    def handle(self, *args, **options):
        infile = options["file"]
        sheet = options["sheet"]
        dry_run = options["dry_run"]
        upsert = options["upsert"]
        match_fields = options["match_fields"]

        # --- Load file (Excel or CSV) ---
        try:
            if infile.lower().endswith(".xlsx"):
                # Ensure we read a single DataFrame (not a dict of sheets)
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

        # If df is a dict (in case sheet_name=None slipped through), grab the first sheet
        if isinstance(df, dict):
            first_key = next(iter(df))
            df = df[first_key]

        if not isinstance(df, pd.DataFrame):
            raise CommandError("Loaded object is not a DataFrame. Check your --sheet argument and file content.")

        # Normalize column names (trim spaces, preserve original case)
        df.columns = [str(c).strip() for c in df.columns]

        # Recognized columns (we'll match case-insensitively)
        amount_col = self._find_col(df, ["Amount"])
        if not amount_col:
            raise CommandError("Missing required 'Amount' column.")

        ay_id_col = self._find_col(df, ["Academic Year ID"])
        gc_id_col = self._find_col(df, ["Grade Class ID"])
        tm_id_col = self._find_col(df, ["Term ID"])

        ay_name_col = self._find_col(df, ["Academic Year"])
        gc_name_col = self._find_col(df, ["Grade/Class", "Grade Class"])  # support both spellings
        tm_name_col = self._find_col(df, ["Term"])

        # Ensure at least one FK column set present
        if not any([ay_id_col, ay_name_col]) or not any([gc_id_col, gc_name_col]) or not any([tm_id_col, tm_name_col]):
            raise CommandError(
                "Provide foreign keys by IDs or by names:\n"
                " - IDs columns: 'Academic Year ID', 'Grade Class ID', 'Term ID'\n"
                " - Name columns: 'Academic Year', 'Grade/Class' (or 'Grade Class'), 'Term'"
            )

        # --- FK resolvers (prefer IDs; fallback to names, case-insensitive) ---
        def resolve_academic_year(row):
            if ay_id_col and pd.notna(row.get(ay_id_col)):
                ay_id = self._coerce_int(row.get(ay_id_col), "Academic Year ID")
                try:
                    return AcademicYear.objects.get(id=ay_id)
                except AcademicYear.DoesNotExist:
                    raise ValueError(f"AcademicYear with ID {ay_id} not found.")
            if ay_name_col and pd.notna(row.get(ay_name_col)):
                name = str(row.get(ay_name_col)).strip()
                try:
                    return AcademicYear.objects.get(name__iexact=name)
                except AcademicYear.DoesNotExist:
                    raise ValueError(f"AcademicYear with name '{name}' not found.")
            raise ValueError("Missing Academic Year (ID or name).")

        def resolve_grade_class(row):
            if gc_id_col and pd.notna(row.get(gc_id_col)):
                gc_id = self._coerce_int(row.get(gc_id_col), "Grade Class ID")
                try:
                    return GradeClass.objects.get(id=gc_id)
                except GradeClass.DoesNotExist:
                    raise ValueError(f"GradeClass with ID {gc_id} not found.")
            if gc_name_col and pd.notna(row.get(gc_name_col)):
                name = str(row.get(gc_name_col)).strip()
                try:
                    return GradeClass.objects.get(name__iexact=name)
                except GradeClass.DoesNotExist:
                    raise ValueError(f"GradeClass with name '{name}' not found.")
            raise ValueError("Missing Grade/Class (ID or name).")

        def resolve_term(row):
            if tm_id_col and pd.notna(row.get(tm_id_col)):
                term_id = self._coerce_int(row.get(tm_id_col), "Term ID")
                try:
                    return Term.objects.get(id=term_id)
                except Term.DoesNotExist:
                    raise ValueError(f"Term with ID {term_id} not found.")
            if tm_name_col and pd.notna(row.get(tm_name_col)):
                name = str(row.get(tm_name_col)).strip()
                try:
                    return Term.objects.get(name__iexact=name)
                except Term.DoesNotExist:
                    raise ValueError(f"Term with name '{name}' not found.")
            raise ValueError("Missing Term (ID or name).")

        # --- Pre-fetch existing for upsert ---
        existing_map = {}
        if upsert:
            # Validate match_fields content
            valid_fields = {"academic_year", "grade_class", "term"}
            if not set(match_fields).issubset(valid_fields):
                raise CommandError(f"--match-fields must be subset of {valid_fields}")
            qs = FeeStructure.objects.select_related("academic_year", "grade_class", "term")
            for fs in qs:
                key = tuple(getattr(fs, f"{f}_id") for f in match_fields)
                existing_map[key] = fs

        to_create, to_update, errors = [], [], []

        # --- Iterate rows ---
        for idx, row in df.iterrows():
            row_no = idx + 2  # human-friendly numbering (account for header)

            # Resolve FKs
            try:
                ay = resolve_academic_year(row)
                gc = resolve_grade_class(row)
                tm = resolve_term(row)
            except ValueError as e:
                errors.append((row_no, str(e)))
                continue

            # Cross-check: Term must belong to the same AcademicYear
            if getattr(tm, "academic_year_id", None) and tm.academic_year_id != ay.id:
                errors.append((row_no, f"Term '{tm.name}' belongs to AcademicYear ID {tm.academic_year_id}, "
                                       f"but row specifies AcademicYear ID {ay.id}."))
                continue

            # Amount
            try:
                amount = self._coerce_decimal(row.get(amount_col), "Amount")
            except ValueError as e:
                errors.append((row_no, str(e)))
                continue

            if upsert:
                lookup_key = tuple(
                    [ay.id if f == "academic_year" else
                     gc.id if f == "grade_class" else
                     tm.id for f in match_fields]
                )
                existing = existing_map.get(lookup_key)
                if existing:
                    existing.amount = amount
                    to_update.append(existing)
                else:
                    to_create.append(FeeStructure(
                        academic_year=ay, grade_class=gc, term=tm, amount=amount
                    ))
            else:
                to_create.append(FeeStructure(
                    academic_year=ay, grade_class=gc, term=tm, amount=amount
                ))

        # --- Report ---
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

        # --- Commit ---
        with transaction.atomic():
            if to_create:
                FeeStructure.objects.bulk_create(to_create, batch_size=500)
            for fs in to_update:
                fs.save(update_fields=["amount"])

        self.stdout.write(self.style.SUCCESS(
            f"Import complete: created {len(to_create)}, updated {len(to_update)}."
        ))
