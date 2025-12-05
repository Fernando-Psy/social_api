from django.db import transaction
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
import os

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    followers_count = serializers.SerializerMethodField(read_only=True)
    following_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "profile_picture",
            "bio",
            "followers_count",
            "following_count",
        ]
        read_only_fields = ["id", "followers_count", "following_count"]
        extra_kwargs = {
            "email": {"required": False},
            "username": {"required": False},
            "first_name": {"required": False},
            "last_name": {"required": False},
            "bio": {"required": False},
            "profile_picture": {"required": False},
        }

    def get_followers_count(self, obj):
        followers = getattr(obj, "followers", None)
        return followers.count() if followers is not None else 0

    def get_following_count(self, obj):
        following = getattr(obj, "following", None)
        return following.count() if following is not None else 0

    def update(self, instance, validated_data):
        new_profile_picture = validated_data.get("profile_picture")
        if new_profile_picture:
            if instance.profile_picture:
                try:
                    if os.path.isfile(instance.profile_picture.path):
                        os.remove(instance.profile_picture.path)
                except Exception as e:
                    print(f"Erro ao deletar a imagem antiga: {str(e)}")
            instance.profile_picture.delete(save=False)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
        validators=[validate_password],
        help_text=_("Senha deve ter no mínimo 8 caracteres e obedecer as regras de segurança"),
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
        help_text=_("Confirme a senha"),
    )

    class Meta:
        model = User
        fields = ["username", "email", "password", "password2", "first_name", "last_name"]
        extra_kwargs = {
            "first_name": {"required": False},
            "last_name": {"required": False},
        }

    def validate_email(self, value):
        """Normaliza e valida se o email já está em uso (case-insensitive)."""
        email = value.strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError(_("Este email já está cadastrado."))
        return email

    def validate_username(self, value):
        """Normaliza e valida se o username já está em uso (case-insensitive)."""
        username = value.strip()
        if User.objects.filter(username__iexact=username).exists():
            raise serializers.ValidationError(_("Este username já está em uso."))
        return username

    def validate(self, attrs):
        """Valida se as senhas coincidem."""
        if attrs.get("password") != attrs.get("password2"):
            raise serializers.ValidationError(
                {"password": _("As senhas não coincidem.")}
                )

        password = attrs.get("password")
        try:
            validate_password(password)
        except Exception as e:
            raise serializers.ValidationError({"password": list(e.messages)})

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        """Cria o usuário garantindo password hashing e atomicidade."""
        validated_data.pop("password2")
        password = validated_data.pop("password")

        # Normalizar email se presente
        if "email" in validated_data and validated_data["email"] is not None:
            validated_data["email"] = validated_data["email"].strip().lower()

        validated_data["username"] = validated_data["username"].strip()
        validated_data["first_name"] = validated_data.get("first_name", "").strip()
        validated_data["last_name"] = validated_data.get("last_name", "").strip()

        user = User.objects.create_user(password=password, **validated_data)
        return user