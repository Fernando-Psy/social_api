from typing import Any, Dict
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from .models import Post, Like, Comment
from users.serializers import UserSerializer


class LikeSerializer(serializers.ModelSerializer):
    """Serializer de Like (somente leitura do usuário)."""
    user = UserSerializer(read_only=True)

    class Meta:
        model = Like
        fields = ['id', 'user', 'created_at']
        read_only_fields = fields


class CommentSerializer(serializers.ModelSerializer):
    """Serializer de Comment (id, usuário e timestamps somente leitura)."""
    user = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'user', 'content', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


class PostSerializer(serializers.ModelSerializer):
    """Serializer de Post com nested serializers para likes e comments."""
    user = UserSerializer(read_only=True)
    likes = LikeSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id', 'user', 'content', 'image',
            'created_at', 'updated_at',
            'likes', 'comments',
            'likes_count', 'comments_count'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
        extra_kwargs = {
            'image': {'required': False, 'allow_null': True},
            'content': {'required': False, 'allow_null': True},
        }

    def get_likes_count(self, obj: Post) -> int:
        """
        Retorna likes_count. Se a queryset foi anotada (ex: .annotate(likes_count=...))
        usa o valor anotado para evitar consultas adicionais.
        """
        annotated = getattr(obj, 'likes_count', None)
        if annotated is not None:
            return int(annotated)
        return obj.likes.count()

    def get_comments_count(self, obj: Post) -> int:
        annotated = getattr(obj, 'comments_count', None)
        if annotated is not None:
            return int(annotated)
        return obj.comments.count()

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validação de nível de objeto: exige ao menos 'content' não vazio ou 'image'.
        Usa dados do request para cobrir upload via multipart (request.data/request.FILES).
        """
        content = attrs.get('content') or ''
        content_stripped = content.strip() if isinstance(content, str) else content
        has_image_in_attrs = attrs.get('image') is not None

        # Em alguns cenários (multipart/form-data) a imagem pode estar em request.data/FILES
        request = self.context.get('request') if isinstance(self.context, dict) else None
        has_image_in_request = False
        if request is not None:
            # request.data pode conter o campo 'image' mesmo que não esteja em attrs
            has_image_in_request = bool(request.data.get('image') or request.FILES.get('image'))

        if not content_stripped and not (has_image_in_attrs or has_image_in_request):
            raise serializers.ValidationError(
                {"non_field_errors": [_("Content or image is required.")]},
                code='required'
            )
        return attrs