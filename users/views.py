from django.contrib.auth import get_user_model, authenticate
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer, UserSerializer
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """
    View para registro de novos usuários
    """
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.save()

            # Gera tokens JWT para login automático
            refresh = RefreshToken.for_user(user)

            headers = self.get_success_headers(serializer.data)

            return Response({
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'message': 'Usuário criado com sucesso!'
            }, status=status.HTTP_201_CREATED, headers=headers)

        except Exception as e:
            return Response({
                'error': str(e),
                'details': serializer.errors if hasattr(serializer, 'errors') else {}
            }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    View para login de usuários
    Aceita username ou email + password
    """
    username_or_email = request.data.get('username')
    password = request.data.get('password')

    # Validação básica
    if not username_or_email or not password:
        return Response({
            'error': 'Username/email e senha são obrigatórios'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Tenta autenticar por username
    user = authenticate(username=username_or_email, password=password)

    # Se não funcionou, tenta por email
    if user is None:
        try:
            user_obj = User.objects.get(email__iexact=username_or_email)
            user = authenticate(username=user_obj.username, password=password)
        except User.DoesNotExist:
            pass

    if user is not None:
        if not user.is_active:
            return Response({
                'error': 'Esta conta está desativada'
            }, status=status.HTTP_403_FORBIDDEN)

        # Gera tokens JWT
        refresh = RefreshToken.for_user(user)

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data,
            'message': 'Login realizado com sucesso!'
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'error': 'Credenciais inválidas'
        }, status=status.HTTP_401_UNAUTHORIZED)


class ProfileUpdateView(APIView):
    """
    View para atualização de perfil do usuário
    """
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Retorna os dados do usuário autenticado"""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        """Atualiza os dados do usuário autenticado"""
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({
                'user': serializer.data,
                'message': 'Perfil atualizado com sucesso!'
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        """Atualização parcial do perfil"""
        return self.put(request, *args, **kwargs)