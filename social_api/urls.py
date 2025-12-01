from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


def api_root(request):
    """View de boas-vindas da API"""
    return JsonResponse({
        'message': 'Bem-vindo à Social API!',
        'version': '1.0',
        'endpoints': {
            'auth': {
                'register': '/api/auth/register/',
                'login': '/api/auth/login/',
                'profile': '/api/auth/profile/',
                'users_list': '/api/auth/list/',
                'token': '/api/token/',
                'token_refresh': '/api/token/refresh/',
            },
            'posts': {
                'list': '/api/posts/',
                'detail': '/api/posts/{id}/',
                'like': '/api/posts/{id}/like/',
                'unlike': '/api/posts/{id}/unlike/',
                'comment': '/api/posts/{id}/comment/',
                'comments': '/api/posts/{id}/comments/',
            },
            'follows': {
                'follow': '/api/follows/users/{id}/follow/',
                'unfollow': '/api/follows/users/{id}/unfollow/',
                'following': '/api/follows/following/',
                'followers': '/api/follows/followers/',
            },
            'admin': '/admin/',
        },
        'status': 'online'
    })


urlpatterns = [
    # Root endpoint
    path('', api_root, name='api-root'),

    # Admin
    path('admin/', admin.site.urls),

    # Auth endpoints
    path('api/auth/', include('users.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # App endpoints
    path('api/posts/', include('posts.urls')),
    path('api/follows/', include('follows.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
else:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)