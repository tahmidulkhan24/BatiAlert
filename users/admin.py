from django.contrib import admin

from .models import SavedArea, SavedSetup, SetupAppliance, UserProfile


admin.site.register(UserProfile)
admin.site.register(SavedSetup)
admin.site.register(SetupAppliance)
admin.site.register(SavedArea)
