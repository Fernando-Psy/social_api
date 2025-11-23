"""URL configuration for the users app."""
from django.urls import path
from . import views

app_name = "users"

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.login_view, name="login"),
    # "me/" deixa claro que é o perfil do usuário autenticado;
    # troque para "profile/<int:pk>/" se for acesso por id
    path("me/", views.ProfileUpdateView.as_view(), name="profile-update"),
]