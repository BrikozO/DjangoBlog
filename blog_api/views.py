from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, filters

from blog.models import Post
from .permissions import IsAuthorOrReadOnly
from .serializers import PostSerializer


# class StandardResultsSetPagination(PageNumberPagination):
#     page_size = 3
#     page_size_query_param = 'page_size'
#     max_page_size = 10


class PostList(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['author']
    search_fields = ['body', 'author__username']
    ordering_fields = ['author_id', 'publish']
    ordering = ['body']


class PostDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthorOrReadOnly]
    # permission_classes = (permissions.IsAdminUser, )


# class UserPostList(generics.ListAPIView):
#     queryset = Post.objects.all()
#     serializer_class = PostSerializer
#
#     def get_queryset(self):
#         user = self.kwargs['username']
#         return Post.objects.filter(author=user)
