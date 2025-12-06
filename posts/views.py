from django.db.models import Count
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import permissions

from .models import Like, Post, Comment
from .serializers import CommentSerializer, PostSerializer
from follows.models import Follow


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


class PostListCreateView(generics.ListCreateAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        following_ids = Follow.objects.filter(
            follower=self.request.user
        ).values_list('followed_id', flat=True)

        # Inclui posts do próprio usuário e de quem ele segue
        user_ids = list(following_ids) + [self.request.user.id]

        # Otimiza queries e adiciona contagens
        return Post.objects.filter(
            user_id__in=user_ids
        ).select_related('user').prefetch_related(
            'likes__user', 'comments__user'
        ).annotate(
            likes_count=Count('likes', distinct=True),
            comments_count=Count('comments', distinct=True)
        ).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        return Post.objects.select_related('user').prefetch_related(
            'likes__user', 'comments__user'
        ).annotate(
            likes_count=Count('likes', distinct=True),
            comments_count=Count('comments', distinct=True)
        )

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            if instance.user != request.user:
                return Response(
                    {'error': 'Você não tem permissão para deletar este post.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            # Não precisa mais deletar arquivo de imagem
            instance.delete()
            return Response(
                {'message': 'Post deletado com sucesso!'},
                status=status.HTTP_204_NO_CONTENT
            )
        except Exception as e:
            print(f"Erro ao deletar o post: {e}")
            return Response(
                {'error': 'Erro ao deletar o post.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PostInteractionView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Post.objects.all()

    def post(self, request, pk):
        """Adiciona like ou comment"""
        try:
            post = get_object_or_404(Post, pk=pk)
            action = request.path.split('/')[-2]  # 'like' ou 'comment'

            if action == 'like':
                like, created = Like.objects.get_or_create(
                    user=request.user,
                    post=post
                )
                if created:
                    return Response(
                        {'message': 'Post curtido!'},
                        status=status.HTTP_201_CREATED
                    )
                return Response({'message': 'Já curtiu este post!'})

            elif action == 'comment':
                content = request.data.get('content', '').strip()

                if not content:
                    return Response(
                        {'error': 'Conteúdo do comentário é obrigatório'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                comment = Comment.objects.create(
                    user=request.user,
                    post=post,
                    content=content
                )

                return Response(
                    CommentSerializer(comment).data,
                    status=status.HTTP_201_CREATED
                )

            return Response(
                {'error': 'Ação inválida'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            print(f"Erro na interação com o post: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def delete(self, request, pk):
        try:
            post = get_object_or_404(Post, pk=pk)
            action = request.path.split('/')[-2]

            if action == 'unlike':
                deleted, _ = Like.objects.filter(
                    user=request.user,
                    post=post
                ).delete()

                if deleted:
                    return Response({'message': 'Like removido!'})
                return Response(
                    {'message': 'Você não curtiu este post'},
                    status=status.HTTP_404_NOT_FOUND
                )

            return Response(
                {'error': 'Ação inválida'},
                status=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            print(f"Erro ao remover interação do post: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )