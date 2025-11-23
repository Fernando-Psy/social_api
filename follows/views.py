from django.shortcuts import get_object_or_404
from django.db import IntegrityError, transaction

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from posts.models import Post, Comment, Like
from posts.serializers import CommentSerializer
from users.serializers import UserSerializer
from users.models import User
from .models import Follow


class FollowUserView(generics.GenericAPIView):
    """
    POST /follows/{user_id}/follow/
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        target_user = get_object_or_404(User, id=user_id)

        if request.user == target_user:
            return Response({'detail': 'You cannot follow yourself.'}, status=status.HTTP_400_BAD_REQUEST)

        # get_or_create is safe enough here; wrap in transaction to be explicit about concurrency
        try:
            with transaction.atomic():
                follow, created = Follow.objects.get_or_create(follower=request.user, followed=target_user)
        except IntegrityError:
            return Response({'detail': 'Could not follow user at this time.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if created:
            return Response({'detail': 'Followed successfully.'}, status=status.HTTP_201_CREATED)
        return Response({'detail': 'Already following.'}, status=status.HTTP_200_OK)


class UnfollowUserView(generics.GenericAPIView):
    """
    DELETE /follows/{user_id}/unfollow/
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request, user_id):
        target_user = get_object_or_404(User, id=user_id)
        deleted, _ = Follow.objects.filter(follower=request.user, followed=target_user).delete()
        if deleted:
            return Response({'detail': 'Unfollowed successfully.'}, status=status.HTTP_200_OK)
        return Response({'detail': 'Not following.'}, status=status.HTTP_204_NO_CONTENT)


class FollowingListView(generics.ListAPIView):
    """
    GET /follows/following/
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    queryset = User.objects.none()

    def get_queryset(self):
        following_ids = Follow.objects.filter(follower=self.request.user).values_list('followed_id', flat=True)
        return User.objects.filter(id__in=following_ids)


class FollowersListView(generics.ListAPIView):
    """
    GET /follows/followers/
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    queryset = User.objects.none()

    def get_queryset(self):
        follower_ids = Follow.objects.filter(followed=self.request.user).values_list('follower_id', flat=True)
        return User.objects.filter(id__in=follower_ids)


class LikePostView(generics.GenericAPIView):
    """
    POST /posts/{pk}/like/
    """
    permission_classes = [IsAuthenticated]
    queryset = Post.objects.all()

    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        try:
            with transaction.atomic():
                like, created = Like.objects.get_or_create(user=request.user, post=post)
        except IntegrityError:
            return Response({'detail': 'Could not like post at this time.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if created:
            return Response({'detail': 'Post liked.'}, status=status.HTTP_201_CREATED)
        return Response({'detail': 'Already liked.'}, status=status.HTTP_200_OK)


class UnlikePostView(generics.GenericAPIView):
    """
    DELETE /posts/{pk}/unlike/
    """
    permission_classes = [IsAuthenticated]
    queryset = Post.objects.all()

    def delete(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        deleted, _ = Like.objects.filter(user=request.user, post=post).delete()
        if deleted:
            return Response({'detail': 'Like removed.'}, status=status.HTTP_200_OK)
        return Response({'detail': 'Like not found.'}, status=status.HTTP_204_NO_CONTENT)


class CommentCreateView(generics.CreateAPIView):
    """
    POST /posts/{post_id}/comments/
    Uses CommentSerializer for validation and response.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = CommentSerializer

    def perform_create(self, serializer):
        post = get_object_or_404(Post, pk=self.kwargs.get('post_id'))
        serializer.save(user=self.request.user, post=post)


class CommentListView(generics.ListAPIView):
    """
    GET /posts/{post_id}/comments/
    """
    permission_classes = [IsAuthenticated]
    serializer_class = CommentSerializer

    def get_queryset(self):
        post_id = self.kwargs.get('post_id')
        # Optionally ensure post exists:
        get_object_or_404(Post, pk=post_id)
        return Comment.objects.filter(post_id=post_id).order_by('-created_at')