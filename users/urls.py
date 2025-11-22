# users/urls.py
from django.urls import path
from .views import RegisterView, login_view, ProfileUpdateView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', login_view, name='login'),
    path('profile/', ProfileUpdateView.as_view(), name='profile-update'),
]