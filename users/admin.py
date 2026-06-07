from django.contrib import admin
from .models import (
    UserProfile,
    SavedSetup,
    SetupAppliance
)


admin.site.register(UserProfile)
admin.site.register(SavedSetup)
admin.site.register(SetupAppliance)