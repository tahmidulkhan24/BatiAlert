from django.urls import path
from . import views

urlpatterns = [
    path(
        'signup/',
        views.signup,
        name='signup'
    ),
    path('login/',views.login_view,name='login'),
    path(
        'dashboard/',
        views.dashboard,
        name='dashboard'
    ),
    path(
        'profile/',
        views.profile,
        name='profile'
    ),
    path('logout/',views.logout_view,name='logout'),
    path(
    "save-setup/",
    views.save_setup,
    name="save_setup"
    ),
    path(
    "get-saved-setup/",
    views.get_saved_setup,
      name="get_saved_setup"
   ),
    path(
        "save-area/",
        views.save_area,
        name="save_area"
    ),
    path(
        "saved-area/<int:saved_area_id>/delete/",
        views.delete_area,
        name="delete_area"
    ),
]
