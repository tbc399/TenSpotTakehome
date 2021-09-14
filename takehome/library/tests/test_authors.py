from rest_framework import status
from rest_framework.test import (
    APIRequestFactory,
    APITestCase,
    force_authenticate
)

from library import models, views
from .test_data_helper import (
    create_author,
    create_book,
    create_genre,
    create_user,
    create_group,
    get_permissions
)


class AuthorsTest(APITestCase):
    
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
    
    def test_retrieve_author(self):
        """
        Get a single author
        """
        create_book(
            title='Book Title 1',
            publish_year=2021,
            genre=create_genre(name='Mystery'),
            authors=[create_author(first_name='Joey', last_name='Jay')]
        )
        
        request = self.factory.get('/authors/')
        force_authenticate(request, user=self.general_user)
        
        view = views.AuthorViewSet.as_view({'get': 'retrieve'})
        
        response = view(request, pk=1)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertDictEqual(
            {
                'id': 1,
                'first_name': 'Joey',
                'last_name': 'Jay',
                'books': [
                    {
                        'id': 1,
                        'title': 'Book Title 1'
                    }
                ]
            },
            response.data
        )
        
    def test_list_authors(self):
        """
        Anyone can get a list of authors
        """
        create_book(
            title='Book Title 1',
            publish_year=2021,
            genre=create_genre(name='Mystery'),
            authors=[create_author(first_name='Joey', last_name='Jay')]
        )
        create_book(
            title='Book Title 2',
            publish_year=2022,
            genre=create_genre(name='Romance'),
            authors=[create_author(first_name='Jane', last_name='Doe')]
        )
        
        request = self.factory.get('/authors/')
        force_authenticate(request, user=self.general_user)
        
        view = views.AuthorViewSet.as_view({'get': 'list'})
        
        response = view(request)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(2, len(response.data))
        self.assertListEqual([
            {
                'id': 1,
                'first_name': 'Joey',
                'last_name': 'Jay',
                'books': [
                    {
                        'id': 1,
                        'title': 'Book Title 1'
                    }
                ]
            },
            {
                'id': 2,
                'first_name': 'Jane',
                'last_name': 'Doe',
                'books': [
                    {
                        'id': 2,
                        'title': 'Book Title 2'
                    }
                ]
            }],
            response.data
        )
    
    def test_editor_create_author(self):
        """
        Editor can create an author
        """
        request = self.factory.post(
            path='/authors/',
            data={
                'first_name': 'Joey',
                'last_name': 'Jay',
                'books': []
            },
            format='json'
        )
        
        force_authenticate(request, user=self.editor_user)
        view = views.AuthorViewSet.as_view({'post': 'create'})
        response = view(request)
        
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertDictEqual(
            {
                'id': 1,
                'first_name': 'Joey',
                'last_name': 'Jay',
                'books': []
            },
            response.data
        )
    
    def test_admin_create_author(self):
        """
        Admin can create an author
        """
        request = self.factory.post(
            path='/authors/',
            data={
                'first_name': 'Joey',
                'last_name': 'Jay',
                'books': []
            },
            format='json'
        )

        force_authenticate(request, user=self.admin_user)
        view = views.AuthorViewSet.as_view({'post': 'create'})
        response = view(request)

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertDictEqual(
            {
                'id': 1,
                'first_name': 'Joey',
                'last_name': 'Jay',
                'books': []
            },
            response.data
        )

    def test_general_cannot_create_author(self):
        """
        General users cannot create an author
        """
        request = self.factory.post(path='/authors/')
        force_authenticate(request, user=self.general_user)
        view = views.AuthorViewSet.as_view({'post': 'create'})
        response = view(request)
        
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
    
    def test_admin_can_update_author(self):
        """
        Administrator has permission to update an author's details
        """
        create_author(first_name='Jane', last_name='Doe')
        
        request = self.factory.patch(
            path='/authors/',
            data={
                'first_name': 'Janet'
            },
            format='json'
        )
        
        force_authenticate(request, user=self.admin_user)
        view = views.AuthorViewSet.as_view({'patch': 'partial_update'})
        response = view(request, pk=1)
        
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertDictEqual(
            {
                'id': 1,
                'first_name': 'Janet',
                'last_name': 'Doe',
                'books': []
            },
            response.data
        )
    
    def test_editor_can_update_author(self):
        """
        Editor has permission to update an author's details
        """
        create_author(first_name='Jane', last_name='Doe')
        create_book()

        request = self.factory.patch(
            path='/authors/',
            data={
                'last_name': 'Dorothy',
                'books': [1]
            },
            format='json'
        )

        force_authenticate(request, user=self.editor_user)
        view = views.AuthorViewSet.as_view({'patch': 'partial_update'})
        response = view(request, pk=1)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertDictEqual(
            {
                'id': 1,
                'first_name': 'Jane',
                'last_name': 'Dorothy',
                'books': [1]
            },
            response.data
        )

    def test_general_cannot_update_author(self):
        """
        General user does not have permission to update an author's details
        """
        request = self.factory.post(path='/authors/')
        force_authenticate(request, user=self.general_user)
        view = views.AuthorViewSet.as_view({'post': 'create'})
        response = view(request)
        
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
    
    def test_admin_can_destroy_author(self):
        """
        Only an admin can delete an author
        """
        create_author()
        request = self.factory.delete(path='/authors/')
        force_authenticate(request, user=self.admin_user)
        view = views.AuthorViewSet.as_view({'delete': 'destroy'})
        response = view(request, pk=1)
        
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEqual(0, len(models.Author.objects.all()))
    
    def test_editor_cannot_destroy_author(self):
        """
        Editor users cannot delete an author
        """
        create_author()
        request = self.factory.delete(path='/authors/')
        force_authenticate(request, user=self.editor_user)
        view = views.AuthorViewSet.as_view({'delete': 'destroy'})
        response = view(request, pk=1)
        
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.assertEqual(1, len(models.Author.objects.all()))
    
    def test_general_cannot_destroy_author(self):
        """
        General users cannot delete an author
        """
        create_author()
        request = self.factory.delete(path='/authors/')
        force_authenticate(request, user=self.general_user)
        view = views.AuthorViewSet.as_view({'delete': 'destroy'})
        response = view(request, pk=1)
        
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.assertEqual(1, len(models.Author.objects.all()))
