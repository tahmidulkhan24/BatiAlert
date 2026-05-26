from django.db import models
from django.contrib.auth.models import User
from core.models import Area


class UserProfile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    area = models.ForeignKey(
        Area,
        on_delete=models.SET_NULL,
        null=True
    )

    battery_capacity = models.IntegerField(
        default=100
    )

    battery_voltage = models.IntegerField(
        default=12
    )

    battery_percentage = models.IntegerField(
        default=100
    )

    def __str__(self):
        return self.user.username
    
class SavedSetup(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    setup_name = models.CharField(
        max_length=100
    )

    appliance_data = models.JSONField()

    def __str__(self):
        return (
            f"{self.user.username} - "
            f"{self.setup_name}"
        )