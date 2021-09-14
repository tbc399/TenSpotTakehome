from rest_framework import status
from rest_framework.test import (
    APIRequestFactory,
    APITestCase,
    force_authenticate
)

from library import models, views
from .test_data_helper import (
    create_genre,
    create_user,
    create_group,
    get_permissions
)


class GenresTest(APITestCase):
    
    def setUp(self):
        
        admin_group = create_group(
            name='Administrator',
            permissions=get_permissions(
                'add_author',
                'change_author',
                'view_author',
                'delete_author',
                'add_book',
                'view_book',
                'change_book',
                'delete_book',
                'add_checkoutleger',
                'change_checkoutleger',
                'view_checkoutleger',
                'delete_checkoutleger',
                'add_genre',
                'change_genre',
                'view_genre',
                'delete_genre',
                'view_user'
            )
        )
        
        editor_group = create_group(
            name='Editor',
            permissions=get_permissions(
                'add_author',
                'change_author',
                'view_author',
                'add_book',
                'change_book',
                'view_book',
                'add_checkoutleger',
                'change_checkoutleger',
                'view_checkoutleger',
                'delete_checkoutleger',
                'add_genre',
                'change_genre',
                'view_genre'
            )
        )
        
        general_group = create_group(
            name='General',
            permissions=get_permissions(
                'view_author',
                'view_book',
                'add_checkoutleger',
                'change_checkoutleger',
                'view_checkoutleger',
                'delete_checkoutleger',
                'view_genre'
            )
        )
        self.general_user = create_user(
            username='general',
            groups=[general_group]
        )
        self.editor_user = create_user(
            username='editor',
            groups=[editor_group]
        )
        self.admin_user = create_user(
            username='admin',
            groups=[admin_group]
        )
        
        self.factory = APIRequestFactory()
    
    def test_list_genres(self):
        """
        Anyone can get a list of genres
        """
        create_genre(name='Mystery')
        create_genre(name='Romance')
        
        request = self.factory.get('/genres/')
        force_authenticate(request, user=self.general_user)
        
        view = views.GenreViewSet.as_view({'get': 'list'})
        
        response = view(request)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(2, len(response.data))
        self.assertListEqual([
            {
                'id': 1,
                'name': 'Mystery'
            },
            {
                'id': 2,
                'name': 'Romance'
            }],
            response.data
        )
    
    def test_editor_create_genre(self):
        """
        Editor can create a genre
        """
        request = self.factory.post(
            path='/genres/',
            data={
                'name': 'Mystery'
            },
            format='json'
        )
        
        force_authenticate(request, user=self.editor_user)
        view = views.GenreViewSet.as_view({'post': 'create'})
        response = view(request)
        
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertDictEqual(
            {
                'id': 1,
                'name': 'Mystery'
            },
            response.data
        )
    
    def test_admin_create_genre(self):
        """
        Admin can create a genre
        """
        request = self.factory.post(
            path='/genres/',
            data={
                'name': 'Romance'
            },
            format='json'
        )
        
        force_authenticate(request, user=self.admin_user)
        view = views.GenreViewSet.as_view({'post': 'create'})
        response = view(request)
        
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertDictEqual(
            {
                'id': 1,
                'name': 'Romance'
            },
            response.data
        )
    
    def test_general_cannot_create_genre(self):
        """
        General users cannot create a genre
        """
        request = self.factory.post(path='/genres/')
        force_authenticate(request, user=self.general_user)
        view = views.GenreViewSet.as_view({'post': 'create'})
        response = view(request)
        
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
    
    def test_admin_can_destroy_genre(self):
        """
        Only an admin can delete a genre
        """
        create_genre()
        request = self.factory.delete(path='/genre/')
        force_authenticate(request, user=self.admin_user)
        view = views.GenreViewSet.as_view({'delete': 'destroy'})
        response = view(request, pk=1)
        
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEqual(0, len(models.Genre.objects.all()))
    
    def test_editor_cannot_destroy_genre(self):
        """
        Editor users cannot delete a genre
        """
        create_genre()
        request = self.factory.delete(path='/genres/')
        force_authenticate(request, user=self.editor_user)
        view = views.GenreViewSet.as_view({'delete': 'destroy'})
        response = view(request, pk=1)
        
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.assertEqual(1, len(models.Genre.objects.all()))
    
    def test_general_cannot_destroy_genre(self):
        """
        General users cannot delete a genre
        """
        create_genre()
        request = self.factory.delete(path='/genres/')
        force_authenticate(request, user=self.general_user)
        view = views.GenreViewSet.as_view({'delete': 'destroy'})
        response = view(request, pk=1)
        
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.assertEqual(1, len(models.Genre.objects.all()))
