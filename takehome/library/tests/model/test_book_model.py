from django.test import TestCase

from library.tests import test_helper


class BookModelTests(TestCase):
    def test_something_about_books(self):
        author = test_helper.create_author()
        genre = test_helper.create_genre()
        book = test_helper.create_book(authors=[author], genre=genre)
        self.fail('just a sample of using the test helpers')
