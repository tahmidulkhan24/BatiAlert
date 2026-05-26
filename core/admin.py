from django.contrib import admin
from .models import (
    Area,
    Appliance,
    Schedule,
    Notice
)


admin.site.register(Area)
admin.site.register(Appliance)
admin.site.register(Schedule)
admin.site.register(Notice)