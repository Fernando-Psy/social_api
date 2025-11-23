import logging
from django.contrib.auth import get_user_model, authenticate
from django.db import transaction
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.exceptions import ValidationError

from .serializers import RegisterSerializer, UserSerializer

logger = logging.getLogger(__name__)
User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """
    View para registro de novos usuários.
    - Usa transaction.atomic para garantir consistência.
    - Retorna tokens para login automático.
    """
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        # Deixa o DRF lidar com ValidationError levantando exceção apropriada
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            user = serializer.save()

        refresh = RefreshToken.for_user(user)
        headers = self.get_success_headers(serializer.data)

        return Response({
            'user': UserSerializer(user, context={'request': request}).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'message': 'Usuário criado com sucesso!'
        }, status=status.HTTP_201_CREATED, headers=headers)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    View para login de usuários.
    Aceita username ou email + password.
    """
    username_or_email = request.data.get('username')
    password = request.data.get('password')

    if not username_or_email or not password:
        return Response({'error': 'Username/email e senha são obrigatórios'},
                        status=status.HTTP_400_BAD_REQUEST)

    # Tenta autenticar por username primeiro (passando request é recomendado)
    user = authenticate(request=request, username=username_or_email, password=password)

    # Se não funcionou, tenta por email (case-insensitive)
    if user is None:
        try:
            user_obj = User.objects.get(email__iexact=username_or_email)
            user = authenticate(request=request, username=user_obj.username, password=password)
        except User.DoesNotExist:
            user = None

    if user is None:
        return Response({'error': 'Credenciais inválidas'},
                        status=status.HTTP_401_UNAUTHORIZED)

    if not user.is_active:
        return Response({'error': 'Esta conta está desativada'},
                        status=status.HTTP_403_FORBIDDEN)

    refresh = RefreshToken.for_user(user)
    return Response({
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'user': UserSerializer(user, context={'request': request}).data,
        'message': 'Login realizado com sucesso!'
    }, status=status.HTTP_200_OK)


class ProfileUpdateView(APIView):
    """
    View para atualização de perfil do usuário autenticado.
    - Suporta form-data/multipart (para upload de avatar, por exemplo).
    - Usa serializer.is_valid(raise_exception=True) para respostas consistentes do DRF.
    """
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        # Atualização completa (ainda mantemos partial=True para tolerância)
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'user': serializer.data,
            'message': 'Perfil atualizado com sucesso!'
        }, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        # Atualização parcial explícita
        return self.put(request, *args, **kwargs)
