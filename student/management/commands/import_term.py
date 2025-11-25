
# fees/management/commands/import_payments.py
import csv
from decimal import Decimal
from django.utils import timezone
from django.core.management.base import BaseCommand, CommandError
from fees.models import Payment
from fees.models import StudentFeeRecord  # adjust if your app structure differs


class Command(BaseCommand):
    help = "Import Payments from CSV. Expected headers: date, amount, payment_method, student_fee_record_id"

    def add_arguments(self, parser):
        parser.add_argument("file_path", type=str, help="Path to fees_payment.csv")
        parser.add_argument("--dry-run", action="store_true", help="Validate only; no DB changes.")

    def handle(self, *args, **options):
        file_path = options["file_path"]
        dry_run = options["dry_run"]

        created_count = 0
        error_count = 0
        processed_count = 0

        try:
            csvfile = open(file_path, newline="", encoding="utf-8")
        except FileNotFoundError:
            raise CommandError(f"File not found: {file_path}")
        except OSError as e:
            raise CommandError(f"Unable to open file '{file_path}': {e}")

        with csvfile:
            reader = csv.DictReader(csvfile)
            if reader.fieldnames is None:
                raise CommandError("CSV has no header row.")
            header = {h.strip().lower(): h for h in reader.fieldnames}

            required_headers = {"date", "amount", "student_fee_record_id"}
            missing = [h for h in required_headers if h not in header]
            if missing:
                raise CommandError(f"Missing required headers: {', '.join(missing)}")

            for row in reader:
                if not any(v and str(v).strip() for v in row.values()):
                    continue
                processed_count += 1
                try:
                    date_raw = row.get(header["date"], "").strip()
                    amount_raw = row.get(header["amount"], "0").strip()
                    payment_method = (row.get(header.get("payment_method", ""), "") or "").strip()
                    record_id_raw = row.get(header["student_fee_record_id"], "").strip()

                    # Parse date
                    try:
                        date = timezone.datetime.strptime(date_raw, "%Y-%m-%d").date() if date_raw else timezone.now().date()
                    except ValueError:
                        date = timezone.now().date()

                    # Parse amount
                    amount = Decimal(amount_raw or "0")

                    # Fetch related StudentFeeRecord
                    try:
                        record = StudentFeeRecord.objects.get(pk=int(record_id_raw))
                    except StudentFeeRecord.DoesNotExist:
                        error_count += 1
                        self.stdout.write(self.style.ERROR(f"[Row {processed_count}] StudentFeeRecord ID {record_id_raw} not found. Skipping."))
                        continue

                    if dry_run:
                        created_count += 1
                        self.stdout.write(self.style.WARNING(
                            f"[Row {processed_count}] Would create payment: Student={record.student.user.full_name} | Amount={amount} | Date={date}"
                        ))
                    else:
                        Payment.objects.create(
                            student_fee_record=record,
                            date=date,
                            amount=amount,
                            payment_method=payment_method or None
                        )
                        created_count += 1
                        self.stdout.write(self.style.SUCCESS(
                            f"[Row {processed_count}] Created payment: Student={record.student.user.full_name} | Amount={amount} | Date={date}"
                        ))

                except Exception as e:
                    error_count += 1
                    self.stdout.write(self.style.ERROR(f"[Row {processed_count}] Unexpected error: {e}."))
                    continue

        action = "DRY-RUN" if dry_run else "IMPORT"
        self.stdout.write(self.style.NOTICE(
            f"\n[{action} SUMMARY] Processed={processed_count} | Created={created_count} | Errors={error_count}"
        ))
