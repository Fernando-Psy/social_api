from django.db.models import Count
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

from .models import Post
from .serializers import PostSerializer
from follows.models import Follow


class IsOwnerOrReadOnly(object):
    """Permissão personalizada para posts"""
    def has_object_permission(self, request, view, obj):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        return obj.user == request.user


class PostListCreateView(generics.ListCreateAPIView):
    """Lista e cria posts"""
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        # Busca IDs de quem o usuário segue
        following_ids = Follow.objects.filter(
            follower=self.request.user
        ).values_list('followed_id', flat=True)

        # Inclui posts do próprio usuário e de quem ele segue
        user_ids = list(following_ids) + [self.request.user.id]

        # Otimiza queries e adiciona contagens
        return Post.objects.filter(
            user_id__in=user_ids
        ).select_related('user').prefetch_related(
            'likes', 'comments__user'
        ).annotate(
            likes_count=Count('likes', distinct=True),
            comments_count=Count('comments', distinct=True)
        ).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Detalhes, atualiza e deleta posts"""
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        return Post.objects.select_related('user').prefetch_related(
            'likes', 'comments__user'
        ).annotate(
            likes_count=Count('likes', distinct=True),
            comments_count=Count('comments', distinct=True)
        )


class PostInteractionView(generics.GenericAPIView):
    """Gerencia likes e comments em posts"""
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Post.objects.all()

    def post(self, request, pk):
        """Adiciona like ou comment"""
        post = self.get_object()
        action = request.path.split('/')[-2]  # 'like' ou 'comment'

        if action == 'like':
            from .models import Like
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
            from .models import Comment
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

            from .serializers import CommentSerializer
            return Response(
                CommentSerializer(comment).data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            {'error': 'Ação inválida'},
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):
        """Remove like"""
        post = self.get_object()
        action = request.path.split('/')[-2]

        if action == 'unlike':
            from .models import Like
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