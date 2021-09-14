from datetime import datetime, timedelta

from django.db import models
from django.contrib.auth.models import User


class Author(models.Model):
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)


class Genre(models.Model):
    name = models.CharField(max_length=64)


class Book(models.Model):
    title = models.CharField(max_length=128)
    publish_year = models.PositiveIntegerField()
    genre = models.ForeignKey(
        Genre,
        null=True,
        on_delete=models.SET_NULL
    )
    authors = models.ManyToManyField(
        Author,
        related_name='books'
    )


def due_date_default():
    """
    Basic date to approximate local time
    """
    return datetime.now().today() + timedelta(weeks=2)


class CheckoutLeger(models.Model):
    """
    A leger to track when books are checked out
    """
    
    class Meta:
        db_table = 'library_checkout_leger'
    
    user = models.ForeignKey(
        User,
        null=True,
        on_delete=models.SET_NULL,
        related_name='checkout_leger',
        editable=False
    )
    book = models.ForeignKey(
        Book,
        null=True,
        on_delete=models.SET_NULL,
        related_name='checkout_leger',
        editable=False
    )
    checkout_time = models.DateTimeField(auto_now_add=True)
    return_time = models.DateTimeField(null=True)
    due_date = models.DateField(default=due_date_default)
