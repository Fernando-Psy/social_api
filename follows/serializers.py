from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Follow
from users.serializers import UserSerializer

User = get_user_model()

class FollowSerializer(serializers.ModelSerializer):
    # representação read-only aninhada
    follower = UserSerializer(read_only=True)
    followed = UserSerializer(read_only=True)

    # campos write-only para criação/atualização
    follower_id = serializers.HiddenField(
        default=serializers.CurrentUserDefault(),
        source='follower',
        write_only=True
    )
    followed_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='followed',
        write_only=True
    )

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
        # validated_data já contém 'follower' e 'followed' por causa de source=...
        return Follow.objects.create(**validated_data)