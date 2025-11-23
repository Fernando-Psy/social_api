from rest_framework import serializers
from .models import Post, Like, Comment
from users.serializers import UserSerializer  # Reutiliza o serializer de User

class LikeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Like
        fields = ['id', 'user', 'created_at']

class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'user', 'content', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']

class PostSerializer(serializers.ModelSerializer):
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

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_comments_count(self, obj):
        return obj.comments.count()

    def validate_content(self, value):
        if not value.strip() and not self.initial_data.get('image'):
            raise serializers.ValidationError("Content or image is required.")
        return value