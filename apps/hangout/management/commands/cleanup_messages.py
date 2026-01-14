from datetime import timedelta, datetime
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from apps.hangout.models import Message


class Command(BaseCommand):
    help = "cleanup hangout messages by count or date"

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            help="cleanup messages older than N days"
        )
        parser.add_argument(
            "--keep",
            type=int,
            help="keep only the most recent N messages"
        )
        parser.add_argument(
            "--before",
            type=str,
            help="cleanup messages before YYYY-MM-DD"
        )
        parser.add_argument(
            "--after",
            type=str,
            help="cleanup messages after YYYY-MM-DD"
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="show what would be done without cleaning up"
        )

    def handle(self, *args, **options):
        days = options["days"]
        keep = options["keep"]
        before = options["before"]
        after = options["after"]
        dry_run = options["dry_run"]

        if not any([days, keep, before, after]):
            raise CommandError("specify --days, --keep, --before or --after")
        if (days or keep) and (before or after):
            raise CommandError("can't combine --days/--keep with --before/--after")
        if days and keep:
            raise CommandError("can't combine --days with --keep")

        if days:
            cutoff = timezone.now() - timedelta(days=days)
            messages = Message.objects.filter(timestamp__lt=cutoff)
            desc = f"older than {days} days"
        elif keep:
            total = Message.objects.count()
            if total <= keep:
                self.stdout.write(self.style.SUCCESS(
                    f"only {total} messages exist, nothing to delete"
                ))
                return
            
            cutoff_messages = Message.objects.order_by("-timestamp")[keep:keep+1].first()
            if cutoff_messages:
                messages = Message.objects.filter(timestamp__lt=cutoff_messages.timestamp)
            else:
                messages = Message.objects.none()
            desc = f"keeping {keep} most recent"
        else:
            messages = Message.objects.all()
            desc_parts = []

            if before:
                try:
                    before_date = timezone.make_aware(datetime.strptime(before, "%Y-%m-%d"))
                    messages = messages.filter(timestamp__lt=before_date)
                    desc_parts.append(f"before {before}")
                except ValueError:
                    raise CommandError("invalid --before date format (use YYYY-MM-DD)")

            if after:
                try:
                    after_date = timezone.make_aware(datetime.strptime(after, "%Y-%m-%d"))
                    messages = messages.filter(timestamp__gt=after_date)
                    desc_parts.append(f"after {after}")
                except ValueError:
                    raise CommandError('Invalid --after date format. Use YYYY-MM-DD')

            desc = " and ".join(desc_parts)

        count = messages.count()

        if dry_run:
            self.stdout.write(self.style.WARNING(
                f"[DRY RUN] would cleanup {count} messages ({desc})"
            )); return
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS("no messages to cleanup"))
            return

        deleted, _ = messages.delete()
        self.stdout.write(self.style.SUCCESS(f"{deleted} messages deleted ({desc})"))
