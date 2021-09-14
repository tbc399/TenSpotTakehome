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


class BooksTest(APITestCase):
    
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

    def test_retrieve_book(self):
        """
        Get a single book
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

        request = self.factory.get('/books/')
        force_authenticate(request, user=self.general_user)
        
        view = views.BookViewSet.as_view({'get': 'retrieve'})
        
        response1 = view(request, pk=1)
        self.assertEqual(status.HTTP_200_OK, response1.status_code)
        self.assertDictEqual(
            {
                'id': 1,
                'title': 'Book Title 1',
                'authors': [
                    {'id': 1, 'first_name': 'Joey', 'last_name': 'Jay'}
                ],
                'publish_year': 2021,
                'genre': {
                    'id': 1,
                    'name': 'Mystery'
                }
            },
            response1.data
        )
        
        response2 = view(request, pk=2)
        self.assertEqual(status.HTTP_200_OK, response2.status_code)
        self.assertDictEqual(
            {
                'id': 2,
                'title': 'Book Title 2',
                'authors': [
                    {'id': 2, 'first_name': 'Jane', 'last_name': 'Doe'}
                ],
                'publish_year': 2022,
                'genre': {
                    'id': 2,
                    'name': 'Romance'
                }
            },
            response2.data
        )

    def test_list_books(self):
        """
        Anyone can get a list of books
        """
        book1 = create_book(
            title='Book Title 1',
            publish_year=2021,
            genre=create_genre(name='Mystery'),
            authors=[create_author(first_name='Joey', last_name='Jay')]
        )
        book2 = create_book(
            title='Book Title 2',
            publish_year=2022,
            genre=create_genre(name='Romance'),
            authors=[create_author(first_name='Jane', last_name='Doe')]
        )

        request = self.factory.get('/books/')
        force_authenticate(request, user=self.general_user)

        view = views.BookViewSet.as_view({'get': 'list'})

        response = view(request)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(2, len(response.data))
        self.assertListEqual([
            {
                'id': 1,
                'title': 'Book Title 1',
                'authors': [
                    {'id': 1, 'first_name': 'Joey', 'last_name': 'Jay'}
                ],
                'publish_year': 2021,
                'genre': {
                    'id': 1,
                    'name': 'Mystery'
                }
            },
            {
                'id': 2,
                'title': 'Book Title 2',
                'authors': [
                    {'id': 2, 'first_name': 'Jane', 'last_name': 'Doe'}
                ],
                'publish_year': 2022,
                'genre': {
                    'id': 2,
                    'name': 'Romance'
                }
            }],
            response.data
        )

    def test_editor_create_book(self):
        """
        Editor can create a book
        """
        create_genre()
        create_author()
        
        request = self.factory.post(
            path='/books/',
            data={
                'title': 'Book Title 1',
                'genre': 1,
                'authors': [1],
                'publish_year': 2021
            },
            format='json'
        )
        
        force_authenticate(request, user=self.editor_user)
        view = views.BookViewSet.as_view({'post': 'create'})
        response = view(request)
        
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertDictEqual(
            {
                'id': 1,
                'title': 'Book Title 1',
                'authors': [
                    1
                ],
                'publish_year': 2021,
                'genre': 1
            },
            response.data
        )

    def test_admin_create_book(self):
        """
        Admin can create a book
        """
        create_genre()
        create_author()

        request = self.factory.post(
            path='/books/',
            data={
                'title': 'Book Title 1',
                'genre': 1,
                'authors': [1],
                'publish_year': 2021
            },
            format='json'
        )

        force_authenticate(request, user=self.admin_user)
        view = views.BookViewSet.as_view({'post': 'create'})
        response = view(request)

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertDictEqual(
            {
                'id': 1,
                'title': 'Book Title 1',
                'authors': [
                    1
                ],
                'publish_year': 2021,
                'genre': 1
            },
            response.data
        )

    def test_general_cannot_create_book(self):
        """
        General users cannot create a book
        """
        request = self.factory.post(path='/books/')
        force_authenticate(request, user=self.general_user)
        view = views.BookViewSet.as_view({'post': 'create'})
        response = view(request)

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_admin_can_update_book(self):
        """
        Administrator has permission to update a book's details
        """
        create_book(
            title='Book Title 1',
            publish_year=2021,
            genre=create_genre(name='Romance'),
            authors=[create_author(first_name='Jane', last_name='Doe')]
        )

        request = self.factory.patch(
            path='/books/',
            data={
                'title': 'Book Title 2',
                'publish_year': 2022
            },
            format='json'
        )

        force_authenticate(request, user=self.admin_user)
        view = views.BookViewSet.as_view({'patch': 'partial_update'})
        response = view(request, pk=1)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertDictEqual(
            {
                'id': 1,
                'title': 'Book Title 2',
                'authors': [
                    1
                ],
                'publish_year': 2022,
                'genre': 1
            },
            response.data
        )

    def test_editor_can_update_book(self):
        """
        Editor has permission to update a book's details
        """
        create_book(
            title='Book Title 2',
            publish_year=2003,
            genre=create_genre(name='Romance'),
            authors=[create_author(first_name='Jane', last_name='Doe')]
        )

        request = self.factory.patch(
            path='/books/',
            data={
                'title': 'Book Title 4',
            },
            format='json'
        )

        force_authenticate(request, user=self.editor_user)
        view = views.BookViewSet.as_view({'patch': 'partial_update'})
        response = view(request, pk=1)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertDictEqual(
            {
                'id': 1,
                'title': 'Book Title 4',
                'authors': [
                    1
                ],
                'publish_year': 2003,
                'genre': 1
            },
            response.data
        )

    def test_general_cannot_update_book(self):
        """
        General user does not have permission to update a book's details
        """
        request = self.factory.post(path='/books/')
        force_authenticate(request, user=self.general_user)
        view = views.BookViewSet.as_view({'post': 'create'})
        response = view(request)

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_admin_can_destroy_book(self):
        """
        Only an admin can delete a book
        """
        create_book(
            title='Book Title 2',
            publish_year=2003,
            genre=create_genre(name='Romance'),
            authors=[create_author(first_name='Jane', last_name='Doe')]
        )

        request = self.factory.delete(path='/books/')
        force_authenticate(request, user=self.admin_user)
        view = views.BookViewSet.as_view({'delete': 'destroy'})
        response = view(request, pk=1)

        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEqual(0, len(models.Book.objects.all()))

    def test_editor_cannot_destroy_book(self):
        """
        Editor users cannot delete a book
        """
        create_book(
            title='Book Title 2',
            publish_year=2003,
            genre=create_genre(name='Romance'),
            authors=[create_author(first_name='Jane', last_name='Doe')]
        )

        request = self.factory.delete(path='/books/')
        force_authenticate(request, user=self.editor_user)
        view = views.BookViewSet.as_view({'delete': 'destroy'})
        response = view(request, pk=1)

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.assertEqual(1, len(models.Book.objects.all()))

    def test_general_cannot_destroy_book(self):
        """
        General users cannot delete a book
        """
        create_book(
            title='Book Title 2',
            publish_year=2003,
            genre=create_genre(name='Romance'),
            authors=[create_author(first_name='Jane', last_name='Doe')]
        )

        request = self.factory.delete(path='/books/')
        force_authenticate(request, user=self.general_user)
        view = views.BookViewSet.as_view({'delete': 'destroy'})
        response = view(request, pk=1)

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.assertEqual(1, len(models.Book.objects.all()))
