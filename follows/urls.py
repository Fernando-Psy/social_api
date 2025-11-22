# follows/urls.py
from django.urls import path
from .views import FollowUserView, UnfollowUserView, FollowingListView, FollowersListView

urlpatterns = [
    path('<int:user_id>/follow/', FollowUserView.as_view(), name='follow-user'),
    path('<int:user_id>/unfollow/', UnfollowUserView.as_view(), name='unfollow-user'),
    path('following/', FollowingListView.as_view(), name='following-list'),
    path('followers/', FollowersListView.as_view(), name='followers-list'),
]