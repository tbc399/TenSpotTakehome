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


class UsersTest(APITestCase):
    
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
            first_name='Dave',
            last_name='Smith',
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
    
    def test_list_users(self):
        """
        Only an admin can get a list of users
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
        create_checkout_leger(book=book1, user=self.general_user, return_time=None)
        create_checkout_leger(book=book2, user=self.general_user, return_time=None)

        request = self.factory.get('/users/')
        force_authenticate(request, user=self.admin_user)
        view = views.UserViewSet.as_view({'get': 'list'})
        response = view(request)
        
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertListEqual([
            {
                'id': 1,
                'first_name': 'Dave',
                'last_name': 'Smith',
                'role': 'General',
                'books': [
                    {
                        'id': 1,
                        'title': 'Book Title 1'
                    },
                    {
                        'id': 2,
                        'title': 'Book Title 2'
                    }
                ]
            },
            {
                'id': 2,
                'first_name': 'Greg',
                'last_name': 'Anderson',
                'role': 'Editor',
                'books': []
            },
            {
                'id': 3,
                'first_name': 'Jake',
                'last_name': 'Rogers',
                'role': 'Administrator',
                'books': []
            }],
            response.data
        )
