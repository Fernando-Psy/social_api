# views.py
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet

from posts.models import Post

class PostInteractionView(GenericViewSet):
    queryset = Post.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        post = self.get_object()
        post.likes.add(request.user)
        return Response({'status': 'post liked'})

    @action(detail=True, methods=['post'])
    def unlike(self, request, pk=None):
        post = self.get_object()
        post.likes.remove(request.user)
        return Response({'status': 'post unliked'})

    @action(detail=True, methods=['post'])
    def comment(self, request, pk=None):
        post = self.get_object()
        comment_text = request.data.get('comment')
        if comment_text:
            post.comments.create(user=request.user, content=comment_text)  # ⚠️ era 'text', mas é 'content'
            return Response({'status': 'comment added'})
        return Response({'error': 'No comment text provided'}, status=400)