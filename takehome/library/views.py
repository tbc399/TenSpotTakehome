from datetime import date, timedelta

from rest_framework import viewsets, mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from .permissions import *
from .serializers import *
from .models import *


class BookViewSet(viewsets.ModelViewSet):
    
    queryset = Book.objects.all()
    permission_classes = (IsAuthenticated, BookPermissions)  # TODO
    
    def get_serializer_class(self):
        if self.action in ('create', 'update', 'destroy', 'partial_update'):
            return BookDeserializer
        return BookSerializer
    
    @action(methods=['POST'], detail=True)
    def checkout(self, request, pk, *args, **kwargs):
        """
        Checkout a book only if it's available, i.e. not already checkout out
        """
        book_is_available = not CheckoutLeger.objects.filter(
            book_id=pk,
            return_time__isnull=True).exists()
        if book_is_available:
            CheckoutLeger.objects.create(user=request.user, book_id=pk)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                data='This book is currently checked out',
                status=status.HTTP_400_BAD_REQUEST
            )
    
    
class CheckoutsViewSet(mixins.ListModelMixin,
                       mixins.RetrieveModelMixin,
                       mixins.UpdateModelMixin,
                       mixins.DestroyModelMixin,
                       viewsets.GenericViewSet):
    
    queryset = CheckoutLeger.objects.select_related('book', 'user').filter(
        return_time__isnull=True)
    serializer_class = CheckoutsSerializer
    permission_classes = (IsAuthenticated, CheckoutPermissions)

    def retrieve(self, request, pk, *args, **kwargs):
        """
        Get a single checked out book if you're the one who checked it out or
        if you're an admin
        """
        user = request.user
        is_admin = user.groups.filter(name='Administrator').exists()
        checkout_entry = self.get_queryset().filter(book_id=pk).first()
        if checkout_entry is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if is_admin or user == checkout_entry.user:
            serializer = self.get_serializer(dict(
                book_id=checkout_entry.book.id,
                book_title=checkout_entry.book.title,
                due_date=checkout_entry.due_date,
                user=dict(
                    id=checkout_entry.user.id,
                    first_name=checkout_entry.user.first_name,
                    last_name=checkout_entry.user.last_name
                )
            ))
            return Response(data=serializer.data)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)

    def list(self, request, *args, **kwargs):
        """
        Return a list of the users checked out books
        """
        entries = [
            dict(
                book_id=leger.book.id,
                book_title=leger.book.title,
                due_date=leger.due_date,
                user=dict(
                    id=leger.user.id,
                    first_name=leger.user.first_name,
                    last_name=leger.user.last_name
                )
            ) for leger in self.get_queryset().filter(user=request.user)]
        serializer = self.get_serializer(entries, many=True)
        return Response(serializer.data)

    def partial_update(self, request, pk, *args, **kwargs):
        """
        Update a checked out book's due date if you're the admin
        """
        user = request.user
        is_admin = user.groups.filter(name='Administrator').exists()
        if is_admin:
            checkout_entry = self.get_queryset().filter(book_id=pk).first()
            serializer = self.get_serializer(
                checkout_entry, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(data=serializer.data)
        else:
            return Response(
                data='Only an administrator can update a due_date',
                status=status.HTTP_403_FORBIDDEN
            )

    def destroy(self, request, pk, *args, **kwargs):
        """
        Return a book if you're the one who checked it out or if you're an
        admin that needs to change the status to returned
        """
        user = request.user
        is_admin = user.groups.filter(name='Administrator').exists()
        checkout_entry = self.get_queryset().filter(book_id=pk).first()
        if checkout_entry is None:
            return Response(
                data='This book is not currently checked out',
                status=status.HTTP_400_BAD_REQUEST
            )
        else:
            if is_admin or checkout_entry.user == user:
                checkout_entry.return_time = datetime.utcnow()
                checkout_entry.save()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(
                    data='Cannot return a book checked out by another user',
                    status=status.HTTP_403_FORBIDDEN
                )

    @action(methods=['GET'], detail=False)
    def overdue(self, request, *args, **kwargs):
        """
        Only as an admin, list all overdue books
        """
        user = request.user
        is_admin = user.groups.filter(name='Administrator').exists()
        if not is_admin:
            return Response(status=status.HTTP_403_FORBIDDEN)
        now = datetime.utcnow()
        leger_entries = self.get_queryset().filter(due_date__lt=now)
        raw_data = [
            dict(
                book_id=entry.book.id,
                book_title=entry.book.title,
                due_date=entry.due_date,
                user=dict(
                    id=entry.user.id,
                    first_name=entry.user.first_name,
                    last_name=entry.user.last_name
                )
            ) for entry in leger_entries]
        serializer = self.get_serializer(data=raw_data, many=True)
        serializer.is_valid()
        return Response(data=serializer.data)


class AuthorViewSet(viewsets.ModelViewSet):
    
    queryset = Author.objects.all()
    permission_classes = (IsAuthenticated, AuthorPermissions)
    
    def get_serializer_class(self):
        if self.action in ('create', 'update', 'destroy', 'partial_update'):
            return AuthorDeserializer
        return AuthorSerializer


class GenreViewSet(mixins.ListModelMixin,
                   mixins.CreateModelMixin,
                   mixins.DestroyModelMixin,
                   viewsets.GenericViewSet):
    
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAuthenticated, GenrePermissions)


class UserViewSet(mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    
    queryset = User.objects.all().prefetch_related(
        'checkout_leger',
        'checkout_leger__book'
    )
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, UserPermissions)
