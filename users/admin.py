from django.contrib import admin
from .models import (
    UserProfile,
    SavedSetup
)


admin.site.register(UserProfile)
admin.site.register(SavedSetup)