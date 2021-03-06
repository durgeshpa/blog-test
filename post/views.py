from django.shortcuts import render, redirect, get_object_or_404


from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly,
                                        AllowAny,)
from rest_framework.response import Response

from rest_framework.views import APIView

from rest_framework.generics import (
    CreateAPIView,
    DestroyAPIView,
    ListAPIView,
    UpdateAPIView,
    RetrieveAPIView,
    RetrieveUpdateAPIView,
    RetrieveUpdateDestroyAPIView,
)

from rest_framework import filters

# from .paggination import PostLimitOffsetPagination

from .models import Post, Comment

from .permissions import IsOwnerOrReadOnly, IsOwner


from .mixins import MultipleFieldLookupMixin


from .serializers import (
    PostCreateOrUpdate,
    PostListSerializer,
    PostDetailSerializer,
    CommentSerializer,
    CommentCreateUpdateSerializer,
    CommentReplySerializer,
)

# Create your views here..


class CreatePostAPIView(APIView):
    """
    post:..

        Creates a new post instance. Returns created post data
        parameters: [title, body,].....

    """

    queryset = Post.objects.all()
    serializer_class = PostCreateOrUpdate
    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request, *args, **kwargs):
        """Create post.."""
        serializer = PostCreateOrUpdate(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(author=request.user)
            return Response(serializer.data, status=200)
        else:
            return Response({"errors": serializer.errors}, status=400)


class ListPostAPIView(ListAPIView):
    """
    get:..

        Returns a list of all existing posts
    """

    queryset = Post.objects.all()
    serializer_class = PostListSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    # pagination_class = PostLimitOffsetPagination


class DetailPostAPIView(RetrieveUpdateDestroyAPIView):
    """
    get:..

        Returns the details of a post instance. Searches post using slug id.
    put:
        Updates an existing post. Returns updated post data
        parameters: [slug, title, body,]
    delete:
        Delete an existing post
        parameters = [id]..
    """

    queryset = Post.objects.all()
    lookup_field = "id"
    serializer_class = PostDetailSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]


class CreateCommentAPIView(APIView):
    """
    post:..

        Create a comment instnace. Returns created comment data
        parameters: [slug, body]
    """

    serializer_class = CommentCreateUpdateSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, id, *args, **kwargs):
        """Create comment on sluge field..."""
        post = get_object_or_404(Post, id=id)
        print(post)
        serializer = CommentCreateUpdateSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(author=request.user, parent=post)
            return Response(serializer.data, status=200)
        else:
            return Response({"errors": serializer.errors}, status=400)


class ListCommentAPIView(APIView):
    """
    get:..

        Returns the list of comments on a particular post
    """

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, id):
        """List cooment ..."""
        post = Post.objects.get(id=id)
        comments = Comment.objects.filter(parent=post)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=200)


class DetailCommentAPIView(MultipleFieldLookupMixin, RetrieveUpdateDestroyAPIView):
    """
    get:..

        Returns the details of a comment instance. Searches comment using comment id and post slug in the url.
    put:
        Updates an existing comment. Returns updated comment data
        parameters: [parent, author, body]
    delete:
        Delete an existing comment
        parameters: [parent, author, body]......
    """

    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    queryset = Comment.objects.all()
    lookup_fields = ["parent", "id"]
    serializer_class = CommentCreateUpdateSerializer


class Replay(APIView):
    """
    post:..

        Create a comment instnace. Returns created comment data
        parameters: [post id, body,comment id]
    """

    serializer_class = CommentReplySerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, id, c_id, *args, **kwargs):
        """Create comment on sluge field..."""
        post = get_object_or_404(Post, id=id)
        comment_replay = get_object_or_404(Comment, id=c_id)
        serializer = CommentReplySerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(author=request.user, parent=post, replay=comment_replay)
            return Response(serializer.data, status=200)
        else:
            return Response({"errors": serializer.errors}, status=400)


class PostListDetailfilter(ListAPIView):

    queryset = Post.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = PostListSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['^slug']

    # '^' Starts-with search.
    # '=' Exact matches.
    # '@' Full-text search. (Currently only supported Django's PostgreSQL backend.)
    # '$' Regex search.

