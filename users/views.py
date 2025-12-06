import traceback
from django.contrib.auth import get_user_model, authenticate
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser

from follows import serializers

from .serializers import RegisterSerializer, UserSerializer

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """Registro de novos usuários"""
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer
    parser_classes = [JSONParser]

    def create(self, request, *args, **kwargs):
        try:
            print(f"Dados recebidos para registro: {request.data}")

            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            user = serializer.save()
            refresh = RefreshToken.for_user(user)

            return Response({
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'message': 'Usuário criado com sucesso!'
            }, status=status.HTTP_201_CREATED)

        except serializers.ValidationError as e:
            print(f"Erro de validação no registro: {e.detail}")
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print(f"Erro no registro: {str(e)}")
            traceback.print_exc()

            return Response(
                {'error': 'Erro ao criar usuário. Tente novamente.'},
                status=status.HTTP_400_BAD_REQUEST
            )


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """Login de usuários"""
    username_or_email = request.data.get('username')
    password = request.data.get('password')

    if not username_or_email or not password:
        return Response(
            {'error': 'Username/email e senha são obrigatórios'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Tenta autenticar por username
    user = authenticate(username=username_or_email, password=password)

    # Se falhar, tenta por email
    if user is None:
        try:
            user_obj = User.objects.get(email__iexact=username_or_email)
            user = authenticate(username=user_obj.username, password=password)
        except User.DoesNotExist:
            pass

    if user is None:
        return Response(
            {'error': 'Credenciais inválidas'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    if not user.is_active:
        return Response(
            {'error': 'Esta conta está desativada'},
            status=status.HTTP_403_FORBIDDEN
        )

    refresh = RefreshToken.for_user(user)

    return Response({
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'user': UserSerializer(user).data,
        'message': 'Login realizado com sucesso!'
    })


class ProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        try:
            user = request.user

            print(f"Request data: {request.data}")

            serializer = UserSerializer(
                user,
                data=request.data,
                partial=True,
                context={'request': request}
            )

            if serializer.is_valid():
                updated_user = serializer.save()
                print(f"Perfil atualizado com sucesso")
                print(f"Profile picture URL: {updated_user.profile_picture}")

                return Response({
                    'user': UserSerializer(updated_user).data,
                    'message': 'Perfil atualizado com sucesso!'
                })

            print(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print(f"Erro ao atualizar perfil: {str(e)}")
            traceback.print_exc()

            return Response(
                {'error': f'Erro ao atualizar perfil: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def put(self, request):
        return self.patch(request)


class UserListView(generics.ListAPIView):
    """Lista todos os usuários (exceto o usuário atual)"""
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_queryset(self):
        return User.objects.exclude(id=self.request.user.id).filter(is_active=True)