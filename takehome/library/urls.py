from . import views

from django.urls import include, path
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'books', views.BookViewSet)
router.register(r'book-checkouts', views.CheckoutsViewSet)
router.register(r'authors', views.AuthorViewSet)
router.register(r'genres', views.GenreViewSet)
router.register(r'users', views.UserViewSet)

app_name = 'library'
urlpatterns = [
    path('', include(router.urls))
]
