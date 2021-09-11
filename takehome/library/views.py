from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action

from django.contrib.auth.models import User

from .permissions import *
from .serializers import *
from .models import *


class BookViewSet(viewsets.ModelViewSet):
    
    queryset = Book.objects.all()
    permission_classes = (IsAuthenticated, BookPermissions)
    
    def get_serializer_class(self):
        if self.action in ('create', 'update', 'destroy', 'partial_update'):
            return BookDeserializer
        return BookSerializer
    
    @action(methods=['POST'], detail=True, url_path='checkout')
    def checkout_book(self, request, *args, **kwargs):
        pass
    
    @action(methods=['POST'], detail=True, url_path='return')
    def return_book(self, request, *args, **kwargs):
        pass
    
    @action(methods=['GET'], detail=False, url_path='my-books')
    def my_books(self, request, *args, **kwargs):
        pass
    
    @action(methods=['GET'], detail=False)
    def overdue(self, request, *args, **kwargs):
        pass


class AuthorViewSet(viewsets.ModelViewSet):
    
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = (IsAuthenticated, AuthorPermissions)


class GenreViewSet(mixins.ListModelMixin,
                   mixins.CreateModelMixin,
                   mixins.DestroyModelMixin,
                   viewsets.GenericViewSet):
    
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAuthenticated, GenrePermissions)


class UserViewSet(mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, UserPermissions)
