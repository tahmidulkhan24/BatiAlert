from django.db import models
from django.contrib.auth.models import User
from core.models import Area,Appliance


class UserProfile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    area = models.ForeignKey(
        Area,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    
    def __str__(self):
        return self.user.username
    


class SavedSetup(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    ips_capacity = models.IntegerField()



    def __str__(self):

        return (
            f"{self.user.username}"
        )
    
class SetupAppliance(models.Model):

    setup = models.ForeignKey(
        SavedSetup,
        on_delete=models.CASCADE,
        related_name="items"
    )

    appliance = models.ForeignKey(
        Appliance,
        on_delete=models.CASCADE
    )

    quantity = models.PositiveIntegerField()

    custom_watt = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    priority = models.PositiveIntegerField()

    def __str__(self):

        return (
            f"{self.appliance.name}"
        )


class SavedArea(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="saved_areas"
    )

    area = models.ForeignKey(
        Area,
        on_delete=models.CASCADE
    )

    label = models.CharField(
        max_length=80,
        default="Home"
    )

    email_alerts = models.BooleanField(
        default=True
    )

    alert_minutes_before = models.PositiveIntegerField(
        default=30
    )

    is_primary = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        unique_together = (
            "user",
            "area",
            "label",
        )

    def __str__(self):

        return (
            f"{self.user.username} - "
            f"{self.label}"
        )
