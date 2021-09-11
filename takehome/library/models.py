from django.conf import settings
from django.db import models


class Author(models.Model):
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)


class Genre(models.Model):
    name = models.CharField(max_length=64)


class Book(models.Model):
    title = models.CharField(max_length=128)
    publish_year = models.IntegerField()
    genre = models.ForeignKey(
        Genre,
        null=True,
        on_delete=models.SET_NULL
    )
    authors = models.ManyToManyField(
        Author,
        related_name='books'
    )

    
class BookCheckout(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL
    )
    book = models.ForeignKey(
        Book,
        null=True,
        on_delete=models.SET_NULL
    )
    checkout_time = models.DateTimeField()
    due_date = models.DateField()
    
    
class BookReturn(models.Model):
    checkout = models.ForeignKey(
        BookCheckout,
        related_name='book_return',
        null=True,
        on_delete=models.SET_NULL
    )
    return_time = models.DateTimeField()
