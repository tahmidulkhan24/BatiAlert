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
]
