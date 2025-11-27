from django.urls import path
from . import views

app_name = "follows"

urlpatterns = [
    path('users/<int:user_id>/follow/', views.FollowUserView.as_view(), name='follow_user'),
    path('users/<int:user_id>/unfollow/', views.UnfollowUserView.as_view(), name='unfollow_user'),
    path('following/', views.FollowingListView.as_view(), name='following_list'),
    path('followers/', views.FollowersListView.as_view(), name='followers_list'),
]