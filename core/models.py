from django.db import models
from django.utils import timezone


class Area(models.Model):

    district = models.CharField(max_length=100)

    upazila = models.CharField(max_length=100)

    area_name = models.CharField(max_length=100)

    def __str__(self):
        return (
            f"{self.district} - "
            f"{self.upazila} - "
            f"{self.area_name}"
        )


class Appliance(models.Model):

    name = models.CharField(
        max_length=100
    )

    watt = models.IntegerField()

    def __str__(self):
        return self.name


class Schedule(models.Model):

    SCHEDULE_TYPES = [
        ('Daily', 'Daily'),
        ('Weekly', 'Weekly'),
    ]

    area = models.ForeignKey(
        Area,
        on_delete=models.CASCADE
    )

    start_time = models.TimeField()

    end_time = models.TimeField()

    schedule_type = models.CharField(
        max_length=50,
        choices=SCHEDULE_TYPES,
        default='Daily'
    )

    day_of_week = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    start_date = models.DateField()

    end_date = models.DateField(
        blank=True,
        null=True
    )

    reason = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        default=timezone.now
    )

    updated_at = models.DateTimeField(
        default=timezone.now
    )

    def __str__(self):
        return (
            f"{self.area} | "
            f"{self.start_time} - "
            f"{self.end_time}"
        )


class Notice(models.Model):

    NOTICE_TYPES = [
        ('Emergency', 'Emergency'),
        ('Maintenance', 'Maintenance'),
        ('General', 'General'),
    ]

    area = models.ForeignKey(
        Area,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    title = models.CharField(
        max_length=200
    )

    message = models.TextField()

    notice_type = models.CharField(
        max_length=50,
        choices=NOTICE_TYPES
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    is_pinned = models.BooleanField(
        default=False
    )

    def __str__(self):
        return self.title


class NoticeRead(models.Model):

    user = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE
    )

    notice = models.ForeignKey(
        Notice,
        on_delete=models.CASCADE
    )

    read_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        unique_together = (
            'user',
            'notice',
        )

    def __str__(self):
        return (
            f"{self.user.username} read "
            f"{self.notice.title}"
        )


class FeedbackReport(models.Model):

    FEEDBACK_TYPES = [
        ('Schedule Issue', 'Schedule Issue'),
        ('Suggestion', 'Suggestion'),
        ('Other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Review', 'In Review'),
        ('Resolved', 'Resolved'),
    ]

    user = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    area = models.ForeignKey(
        Area,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    feedback_type = models.CharField(
        max_length=50,
        choices=FEEDBACK_TYPES,
        default='Schedule Issue'
    )

    subject = models.CharField(
        max_length=200
    )

    message = models.TextField()

    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    staff_note = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.subject


class OutageNotificationLog(models.Model):

    user = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE
    )

    schedule = models.ForeignKey(
        Schedule,
        on_delete=models.CASCADE
    )

    scheduled_for = models.DateTimeField()

    sent_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        unique_together = (
            'user',
            'schedule',
            'scheduled_for',
        )

    def __str__(self):
        return (
            f"{self.user.email} - "
            f"{self.scheduled_for}"
        )
