from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from users.models import User
from users.serializers import UserSerializer
from posts.models import Post, Comment
from posts.serializers import CommentSerializer
from .models import Follow


class FollowUserView(generics.GenericAPIView):
    """Seguir um usuário"""
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        target_user = get_object_or_404(User, id=user_id)

        if request.user == target_user:
            return Response(
                {'error': 'Você não pode seguir a si mesmo'},
                status=status.HTTP_400_BAD_REQUEST
            )

        follow, created = Follow.objects.get_or_create(
            follower=request.user,
            followed=target_user
        )

        if created:
            return Response(
                {'message': 'Agora você segue este usuário'},
                status=status.HTTP_201_CREATED
            )

        return Response({'message': 'Você já segue este usuário'})


class UnfollowUserView(generics.GenericAPIView):
    """Deixar de seguir um usuário"""
    permission_classes = [IsAuthenticated]

    def delete(self, request, user_id):
        target_user = get_object_or_404(User, id=user_id)

        deleted, _ = Follow.objects.filter(
            follower=request.user,
            followed=target_user
        ).delete()

        if deleted:
            return Response({'message': 'Você deixou de seguir este usuário'})

        return Response(
            {'message': 'Você não seguia este usuário'},
            status=status.HTTP_404_NOT_FOUND
        )


class FollowingListView(generics.ListAPIView):
    """Lista usuários que o usuário atual segue"""
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_queryset(self):
        following_ids = Follow.objects.filter(
            follower=self.request.user
        ).values_list('followed_id', flat=True)

        return User.objects.filter(id__in=following_ids)


class FollowersListView(generics.ListAPIView):
    """Lista seguidores do usuário atual"""
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_queryset(self):
        follower_ids = Follow.objects.filter(
            followed=self.request.user
        ).values_list('follower_id', flat=True)

        return User.objects.filter(id__in=follower_ids)


class CommentListView(generics.ListAPIView):
    """Lista comentários de um post"""
    permission_classes = [IsAuthenticated]
    serializer_class = CommentSerializer

    def get_queryset(self):
        post_id = self.kwargs.get('pk')
        get_object_or_404(Post, pk=post_id)

        return Comment.objects.filter(
            post_id=post_id
        ).select_related('user').order_by('-created_at')