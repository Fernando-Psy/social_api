# /mnt/projetos/social_api/posts/views.py
from django.db import transaction
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Post
from .serializers import PostSerializer
from follows.models import Follow


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Allow read to everyone (handled by IsAuthenticated on the view),
    but only the post owner may update/delete.
    """
    def has_object_permission(self, request, view, obj):
        # Safe methods handled elsewhere; for object-level checks require ownership
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


class PostViewSet(viewsets.ModelViewSet):
    """
    CRUD + interaction endpoints (like, unlike, comment) for Post.
    Uses a single viewset so routing and permissions are consistent.
    """
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        # Use select_related / prefetch_related to avoid N+1 queries
        qs = Post.objects.select_related('user').prefetch_related('likes', 'comments__user').order_by('-created_at')
        # For list view, show posts from people the user follows plus their own posts
        if self.action == 'list':
            following_ids = Follow.objects.filter(follower=self.request.user).values_list('followed_id', flat=True)
            user_ids = list(following_ids) + [self.request.user.id]
            return qs.filter(user__in=user_ids)
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        post = self.get_object()
        post.likes.add(request.user)
        return Response(self.get_serializer(post).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def unlike(self, request, pk=None):
        post = self.get_object()
        post.likes.remove(request.user)
        return Response(self.get_serializer(post).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def comment(self, request, pk=None):
        post = self.get_object()
        comment_text = (request.data.get('comment') or '').strip()
        if not comment_text:
            return Response({'error': 'No comment text provided'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            comment = post.comments.create(user=request.user, text=comment_text)

        # Optionally return the created comment or the updated post representation
        return Response(self.get_serializer(post).data, status=status.HTTP_201_CREATED)