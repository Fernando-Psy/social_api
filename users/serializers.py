from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name',
                  'profile_picture', 'bio', 'followers_count', 'following_count']
        read_only_fields = ['id']

    def get_followers_count(self, obj):
        return obj.followers.count()

    def get_following_count(self, obj):
        return obj.following.count()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        min_length=8,
        help_text="Senha deve ter no mínimo 8 caracteres"
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text="Confirme a senha"
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'first_name', 'last_name']
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': False},
            'last_name': {'required': False}
        }

    def validate_email(self, value):
        """Valida se o email já está em uso"""
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Este email já está cadastrado.")
        return value.lower()

    def validate_username(self, value):
        """Valida se o username já está em uso"""
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("Este username já está em uso.")
        return value

    def validate(self, attrs):
        """Valida se as senhas coincidem"""
        if attrs.get('password') != attrs.get('password2'):
            raise serializers.ValidationError({
                "password": "As senhas não coincidem."
            })
        return attrs

    def create(self, validated_data):
        """Cria o usuário com senha hasheada"""
        # Remove password2 dos dados validados
        validated_data.pop('password2', None)

        # Usa create_user para garantir que a senha seja hasheada corretamente
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user