from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxLengthValidator

class User(AbstractUser):
    profile_picture = models.ImageField(
        upload_to='profile_pics/',
        blank=True,
        null=True,
        help_text="Foto de perfil do usuário.",
        validators=[MaxLengthValidator(1024)]
    )
    bio = models.TextField(
        blank=True,
        null=True,
        max_length=500,
        help_text="Breve descrição sobre o usuário."
    )

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    # Métodos
    def __str__(self):
        return f"{self.username} ({self.email})"

    def get_full_name(self):
        """Retorna o nome completo, se disponível."""
        full_name = super().get_full_name()
        return full_name if full_name.strip() else self.username

    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"
        ordering = ['username']
        db_table = 'custom_user'