from django.db import models


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

    def __str__(self):
        return self.title