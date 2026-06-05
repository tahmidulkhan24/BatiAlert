from django.contrib import admin
from django.urls import path, include

admin.site.site_header = "BatiAlert Administration"

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', include('core.urls')),
    path('users/', include('users.urls')),
]