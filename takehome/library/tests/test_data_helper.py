import random
import datetime

from django.contrib.auth import get_user_model, models
from django.contrib.auth.models import Group, Permission

from library import models
from library.tests.faker import faker

'''
Assumes there are three models:
    Author
    Book
    Genre

Each `create_model` method can take any keyword arguments
to create an instance of a model.
Some defaults are provided in case no arguments are passed in.
Passed in arguments will override the defaults.
'''


def create_author(**kwargs):
    defaults = dict(
        first_name=faker.first_name(),
        last_name=faker.last_name(),
    )
    if kwargs:
        defaults.update(kwargs)
    return models.Author.objects.create(**defaults)


def create_book(authors=None, **kwargs):
    defaults = dict(
        title=faker.bs().title(),
        publish_year=random.randint(1900, 2021),
        genre=kwargs.pop('genre', None) or create_genre(),
    )
    if kwargs:
        defaults.update(kwargs)
    book = models.Book.objects.create(**defaults)
    authors = authors or [create_author()]
    book.authors.set(authors)
    return book


def create_genre(**kwargs):
    defaults = dict(
        name=faker.music_subgenre(),
    )
    if kwargs:
        defaults.update(kwargs)
    return models.Genre.objects.create(**defaults)


def create_user(groups=None, **kwargs):
    model = get_user_model()
    first_name = faker.first_name()
    last_name = faker.last_name()
    username = f'{first_name}{last_name[:1]}{random.randint(100,999)}'
    defaults = dict(
        username=username,
        first_name=first_name,
        last_name=last_name,
        password='12345',
    )
    if kwargs:
        defaults.update(kwargs)
    user = model.objects.create_user(**defaults)
    user.groups.set(groups or list())
    return user


def create_group(permissions=None, **kwargs):
    defaults = dict(
        name='General',
    )
    if kwargs:
        defaults.update(**kwargs)
    group = Group.objects.create(**defaults)
    permissions = permissions or list()
    group.permissions.set(permissions)
    return group


def get_permissions(*codenames):
    return Permission.objects.filter(codename__in=codenames)


def create_checkout_leger(book=None, user=None, **kwargs):
    defaults = dict(
        checkout_time=datetime.datetime.now(),
        return_time=datetime.datetime.now() + datetime.timedelta(days=2),
        due_date=datetime.date.today() + datetime.timedelta(weeks=2),
        book=book or create_book(),
        user=user or create_user()
    )
    if kwargs:
        defaults.update(**kwargs)
    return models.CheckoutLeger.objects.create(**defaults)