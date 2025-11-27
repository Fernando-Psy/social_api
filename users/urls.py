"""URL configuration for the users app."""
from django.urls import path
from . import views

app_name = "users"

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.login_view, name="login"),
    path("profile/", views.ProfileUpdateView.as_view(), name="profile-update"),
]