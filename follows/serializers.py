from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Follow

User = get_user_model()

class FollowSerializer(serializers.ModelSerializer):
    follower = serializers.SerializerMethodField(read_only=True)
    followed = serializers.SerializerMethodField(read_only=True)

    def get_follower(self, obj):
        from users.serializers import UserSerializer
        return UserSerializer(obj.follower).data

    def get_followed(self, obj):
        from users.serializers import UserSerializer
        return UserSerializer(obj.followed).data

    class Meta:
        model = Follow
        fields = ['id', 'follower', 'followed', 'follower_id', 'followed_id', 'created_at']
        read_only_fields = ['id', 'follower', 'followed', 'created_at']

    def validate(self, attrs):
        follower = attrs.get('follower')
        followed = attrs.get('followed')
        if follower == followed:
            raise serializers.ValidationError("Você não pode seguir a si mesmo.")
        if Follow.objects.filter(follower=follower, followed=followed).exists():
            raise serializers.ValidationError("Já está seguindo este usuário.")
        return attrs

    def create(self, validated_data):
        return Follow.objects.create(**validated_data)