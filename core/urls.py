from django.urls import path
from . import views

urlpatterns = [
    path(
        '',
        views.home,
        name='home'
    ),

    path(
        'schedule/',
        views.schedule,
        name='schedule'
    ),

    path(
        'ajax/get-upazilas/',
        views.get_upazilas,
        name='get_upazilas'
    ),

    path(
        'ajax/get-areas/',
        views.get_areas,
        name='get_areas'
    ),

    path(
        'notice/',
        views.notice_view,
        name='notices'
    ),
]