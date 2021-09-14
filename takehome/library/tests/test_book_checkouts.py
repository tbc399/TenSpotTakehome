import datetime

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
    get_permissions,
    create_checkout_leger
)


class CheckoutsTests(APITestCase):
    
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
        self.general_user_1 = create_user(
            username='general1',
            first_name='Dave',
            last_name='Smith',
            groups=[general_group]
        )
        self.general_user_2 = create_user(
            username='general2',
            first_name='Frank',
            last_name='Collins',
            groups=[general_group]
        )
        self.editor_user = create_user(
            username='editor',
            first_name='Greg',
            last_name='Anderson',
            groups=[editor_group]
        )
        self.admin_user = create_user(
            username='admin',
            first_name='Jake',
            last_name='Rogers',
            groups=[admin_group]
        )
        
        self.factory = APIRequestFactory()
    
    def test_user_checked_out_books(self):
        """
        A user can only see a list of the books they currently have checked out
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
        book3 = create_book(
            title='Book Title 3',
            publish_year=2022,
            genre=create_genre(name='Romance'),
            authors=[create_author(first_name='Jane', last_name='Doe')]
        )
        book4 = create_book(
            title='Book Title 4',
            publish_year=2022,
            genre=create_genre(name='Biography'),
            authors=[create_author(first_name='Jane', last_name='Doe')]
        )
        due_date = datetime.date.today() + datetime.timedelta(days=2)
        create_checkout_leger(
            book=book1,
            user=self.general_user_1,
            return_time=None,
            due_date=due_date
        )
        create_checkout_leger(
            book=book2,
            user=self.general_user_1,
            return_time=None,
            due_date=due_date
        )
        create_checkout_leger(
            book=book3,
            user=self.general_user_2,
            return_time=None,
            due_date=due_date
        )
        create_checkout_leger(
            book=book4,
            user=self.editor_user,
            return_time=None,
            due_date=due_date
        )

        request = self.factory.get('/book-checkouts/')
        force_authenticate(request, user=self.general_user_1)
        view = views.CheckoutsViewSet.as_view({'get': 'list'})
        response = view(request)
        
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertListEqual([
            {
                'book_id': 1,
                'book_title': 'Book Title 1',
                'due_date': str(due_date),
                'user': {
                    'id': 1,
                    'first_name': 'Dave',
                    'last_name': 'Smith'
                }
            },
            {
                'book_id': 2,
                'book_title': 'Book Title 2',
                'due_date': str(due_date),
                'user': {
                    'id': 1,
                    'first_name': 'Dave',
                    'last_name': 'Smith'
                }
            }],
            response.data
        )

    def test_checkout_successful(self):
        """
        A basic successful checkout of a book
        """
        book1 = create_book(
            title='Book Title 1',
            publish_year=2021,
            genre=create_genre(name='Mystery'),
            authors=[create_author(first_name='Joey', last_name='Jay')]
        )
        
        request1 = self.factory.post('/books/1/checkout/')
        force_authenticate(request1, user=self.general_user_2)
        view = views.BookViewSet.as_view({'post': 'checkout'})
        response = view(request1, pk=1)
        
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        
        request2 = self.factory.get('/book-checkouts/')
        force_authenticate(request2, user=self.general_user_2)
        view = views.CheckoutsViewSet.as_view({'get': 'list'})
        response = view(request2)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertListEqual([
            {
                'book_id': 1,
                'book_title': 'Book Title 1',
                'due_date': str(datetime.date.today() + datetime.timedelta(weeks=2)),
                'user': {
                    'id': 2,
                    'first_name': 'Frank',
                    'last_name': 'Collins'
                }
            }],
            response.data
        )

    def test_checkout_failure(self):
        """
        Try to checkout a book, but it fails because it's already checkout out
        """
        create_book(
            title='Book Title 1',
            publish_year=2021,
            genre=create_genre(name='Mystery'),
            authors=[create_author(first_name='Joey', last_name='Jay')]
        )

        request1 = self.factory.post('/books/1/checkout/')
        force_authenticate(request1, user=self.general_user_1)
        view = views.BookViewSet.as_view({'post': 'checkout'})
        response = view(request1, pk=1)

        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        
        request2 = self.factory.post('/books/1/checkout/')
        force_authenticate(request2, user=self.general_user_2)
        view = views.BookViewSet.as_view({'post': 'checkout'})
        response = view(request2, pk=1)

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_return_successful(self):
        """
        Return a book that you have checked out
        """
        create_book(
            title='Book Title 1',
            publish_year=2021,
            genre=create_genre(name='Mystery'),
            authors=[create_author(first_name='Joey', last_name='Jay')]
        )

        request1 = self.factory.post('/books/1/checkout/')
        force_authenticate(request1, user=self.general_user_1)
        view = views.BookViewSet.as_view({'post': 'checkout'})
        response = view(request1, pk=1)

        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)

        request2 = self.factory.delete('/book-checkouts/')
        force_authenticate(request2, user=self.general_user_1)
        view = views.CheckoutsViewSet.as_view({'delete': 'destroy'})
        response = view(request2, pk=1)

        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)

    def test_return_failure(self):
        """
        Cannot return a book that you don't have checked out
        """
        create_book(
            title='Book Title 1',
            publish_year=2021,
            genre=create_genre(name='Mystery'),
            authors=[create_author(first_name='Joey', last_name='Jay')]
        )

        request1 = self.factory.post('/books/1/checkout/')
        force_authenticate(request1, user=self.general_user_1)
        view = views.BookViewSet.as_view({'post': 'checkout'})
        response = view(request1, pk=1)

        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)

        request2 = self.factory.delete('/book-checkouts/')
        force_authenticate(request2, user=self.general_user_2)
        view = views.CheckoutsViewSet.as_view({'delete': 'destroy'})
        response = view(request2, pk=1)

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_return_as_admin(self):
        """
        An admin has the ability to return a book for another user
        """
        create_book(
            title='Book Title 1',
            publish_year=2021,
            genre=create_genre(name='Mystery'),
            authors=[create_author(first_name='Joey', last_name='Jay')]
        )

        request1 = self.factory.post('/books/1/checkout/')
        force_authenticate(request1, user=self.general_user_1)
        view = views.BookViewSet.as_view({'post': 'checkout'})
        response = view(request1, pk=1)

        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)

        request2 = self.factory.delete('/book-checkouts/')
        force_authenticate(request2, user=self.admin_user)
        view = views.CheckoutsViewSet.as_view({'delete': 'destroy'})
        response = view(request2, pk=1)

        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)

    def test_admin_change_due_date(self):
        """
        An admin can change a due date
        """
        create_book(
            title='Book Title 1',
            publish_year=2021,
            genre=create_genre(name='Mystery'),
            authors=[create_author(first_name='Joey', last_name='Jay')]
        )

        request1 = self.factory.post('/books/1/checkout/')
        force_authenticate(request1, user=self.general_user_1)
        view = views.BookViewSet.as_view({'post': 'checkout'})
        response = view(request1, pk=1)

        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        
        request2 = self.factory.patch(
            '/book-checkouts/',
            data={'due_date': '2021-04-12'},
            format='json'
        )
        force_authenticate(request2, user=self.admin_user)
        view = views.CheckoutsViewSet.as_view({'patch': 'partial_update'})
        response = view(request2, pk=1)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(
            datetime.date(year=2021, month=4, day=12),
            models.CheckoutLeger.objects.first().due_date
        )

    def test_overdue_books(self):
        """
        An admin can view a list of overdue books
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
        book3 = create_book(
            title='Book Title 3',
            publish_year=2022,
            genre=create_genre(name='Romance'),
            authors=[create_author(first_name='Jane', last_name='Doe')]
        )
        book4 = create_book(
            title='Book Title 4',
            publish_year=2022,
            genre=create_genre(name='Biography'),
            authors=[create_author(first_name='Jane', last_name='Doe')]
        )
        create_checkout_leger(
            book=book1,
            user=self.general_user_1,
            checkout_time=datetime.datetime.now() - datetime.timedelta(weeks=1),
            return_time=None,
            due_date=datetime.date.today() - datetime.timedelta(days=2)
        )
        create_checkout_leger(
            book=book2,
            user=self.general_user_1,
            return_time=None
        )
        create_checkout_leger(
            book=book3,
            user=self.general_user_2,
            return_time=None
        )
        create_checkout_leger(
            book=book4,
            user=self.editor_user,
            checkout_time=datetime.datetime.now() - datetime.timedelta(weeks=1),
            return_time=None,
            due_date=datetime.date.today() - datetime.timedelta(days=2)
        )

        request = self.factory.get('/book-checkouts/overdue')
        force_authenticate(request, user=self.admin_user)
        view = views.CheckoutsViewSet.as_view({'get': 'overdue'})
        response = view(request)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertListEqual([
            {
                'book_id': 1,
                'book_title': 'Book Title 1',
                'due_date': str(datetime.date.today() - datetime.timedelta(days=2)),
                'user': {
                    'id': 1,
                    'first_name': 'Dave',
                    'last_name': 'Smith'
                }
            },
            {
                'book_id': 4,
                'book_title': 'Book Title 4',
                'due_date': str(datetime.date.today() - datetime.timedelta(days=2)),
                'user': {
                    'id': 3,
                    'first_name': 'Greg',
                    'last_name': 'Anderson'
                }
            }],
            response.data
        )
