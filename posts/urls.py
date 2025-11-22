from django.urls import path

from follows.views import CommentListView
from .views import PostListCreateView, PostDetailView, PostInteractionView

urlpatterns = [
    path('', PostListCreateView.as_view(), name='post-list-create'),
    path('<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('<int:pk>/like/', PostInteractionView.as_view(), name='post-like'),
    path('<int:pk>/unlike/', PostInteractionView.as_view(), name='post-unlike'),
    path('<int:pk>/comment/', PostInteractionView.as_view(), name='post-comment'),
    path('<int:post_id>/comments/', CommentListView.as_view(), name='comment-list'),
]