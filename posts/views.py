from rest_framework import generics, permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Post
from .serializers import PostSerializer
from follows.models import Follow

class PostListCreateView(generics.ListCreateAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        following_ids = Follow.objects.filter(follower=self.request.user).values_list('followed_id', flat=True)
        return Post.objects.filter(user__in=following_ids).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Post.objects.filter(user=self.request.user)

class PostInteractionView(generics.GenericAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    @api_view(['POST'])
    def like(self, request, pk):
        post = self.get_object()
        post.likes.add(request.user)
        post.save()
        return Response({'status': 'post liked'})

    @api_view(['POST'])
    def unlike(self, request, pk):
        post = self.get_object()
        post.likes.remove(request.user)
        post.save()
        return Response({'status': 'post unliked'})

    @api_view(['POST'])
    def comment(self, request, pk):
        post = self.get_object()
        comment_text = request.data.get('comment')
        if comment_text:
            post.comments.create(user=request.user, text=comment_text)
            return Response({'status': 'comment added'})
        return Response({'error': 'No comment text provided'}, status=400)