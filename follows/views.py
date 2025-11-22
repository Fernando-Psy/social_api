from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from posts.models import Comment, Post
from posts.serializers import CommentSerializer
from users.serializers import UserSerializer
from .models import Follow
from users.models import User
from rest_framework.decorators import action

class FollowUserView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        try:
            target_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        if request.user == target_user:
            return Response({'error': 'You cannot follow yourself'}, status=status.HTTP_400_BAD_REQUEST)

        follow, created = Follow.objects.get_or_create(follower=request.user, followed=target_user)
        if created:
            return Response({'message': 'Followed successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'message': 'Already following'}, status=status.HTTP_200_OK)

class UnfollowUserView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, user_id):
        try:
            target_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        Follow.objects.filter(follower=request.user, followed=target_user).delete()
        return Response({'message': 'Unfollowed successfully'}, status=status.HTTP_200_OK)

class FollowingListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_queryset(self):
        following_ids = Follow.objects.filter(follower=self.request.user).values_list('followed_id', flat=True)
        return User.objects.filter(id__in=following_ids)

class FollowersListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_queryset(self):
        follower_ids = Follow.objects.filter(followed=self.request.user).values_list('follower_id', flat=True)
        return User.objects.filter(id__in=follower_ids)

class PostInteractionView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Post.objects.all()

    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        post = self.get_object()
        like, created = Like.objects.get_or_create(user=request.user, post=post)
        if created:
            return Response({'message': 'Liked'}, status=status.HTTP_201_CREATED)
        return Response({'message': 'Already liked'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['delete'])
    def unlike(self, request, pk=None):
        post = self.get_object()
        Like.objects.filter(user=request.user, post=post).delete()
        return Response({'message': 'Unliked'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def comment(self, request, pk=None):
        post = self.get_object()
        content = request.data.get('content')
        if not content:
            return Response({'error': 'Content is required'}, status=status.HTTP_400_BAD_REQUEST)
        comment = Comment.objects.create(user=request.user, post=post, content=content)
        return Response(CommentSerializer(comment).data, status=status.HTTP_201_CREATED)

class CommentListView(generics.ListAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        post_id = self.kwargs['post_id']
        return Comment.objects.filter(post_id=post_id).order_by('-created_at')