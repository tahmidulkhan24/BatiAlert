from datetime import datetime, timedelta

from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils import timezone

from core.models import OutageNotificationLog, Schedule
from users.models import SavedArea


class Command(BaseCommand):
    help = "Send email alerts before scheduled outages."

    def handle(self, *args, **options):
        now = timezone.localtime()
        sent_count = 0

        saved_areas = (
            SavedArea.objects
            .filter(email_alerts=True, user__email__gt="")
            .select_related("user", "area")
        )

        for saved_area in saved_areas:
            alert_time = now + timedelta(
                minutes=saved_area.alert_minutes_before
            )

            schedules = (
                Schedule.objects
                .filter(area=saved_area.area)
                .filter(start_date__lte=alert_time.date())
                .filter(
                    Q(end_date__isnull=True) |
                    Q(end_date__gte=alert_time.date())
                )
                .filter(start_time__hour=alert_time.hour)
                .filter(start_time__minute=alert_time.minute)
            )

            for schedule in schedules:
                if schedule.schedule_type == "Weekly":
                    if schedule.day_of_week != alert_time.strftime("%A"):
                        continue

                scheduled_for = timezone.make_aware(
                    datetime.combine(
                        alert_time.date(),
                        schedule.start_time
                    )
                )

                _, created = OutageNotificationLog.objects.get_or_create(
                    user=saved_area.user,
                    schedule=schedule,
                    scheduled_for=scheduled_for
                )

                if not created:
                    continue

                send_mail(
                    subject="Upcoming BatiAlert outage",
                    message=(
                        f"Power is scheduled to be off in "
                        f"{saved_area.area.area_name} from "
                        f"{schedule.start_time} to {schedule.end_time}. "
                        f"Reason: {schedule.reason or 'Not specified'}."
                    ),
                    from_email=None,
                    recipient_list=[saved_area.user.email],
                    fail_silently=False
                )
                sent_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Sent {sent_count} outage notifications."
            )
        )
