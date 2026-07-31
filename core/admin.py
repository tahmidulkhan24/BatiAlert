from django.contrib import admin
from .models import (
    Area,
    Appliance,
    Schedule,
    Notice,
    NoticeRead,
    FeedbackReport,
    OutageNotificationLog
)


admin.site.register(Area)
admin.site.register(Appliance)
admin.site.register(Schedule)
admin.site.register(Notice)
admin.site.register(NoticeRead)
admin.site.register(FeedbackReport)
admin.site.register(OutageNotificationLog)
