from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from ..models import Book, Author, Language, Genre, Borrowing, BookCopy
from datetime import date
from django.urls import reverse

class RegisterAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('api-register')


    def test_register_valid_data(self):
        data = {
            'username': 'testuser',
            'password': 'testpassword',
            'email': 'test@gmail.com'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user', response.data)
        self.assertIn('token', response.data)

        self.assertEqual(response.data['user']['username'], data['username'])
        self.assertEqual(response.data['user']['email'], data['email'])

    def test_register_existing_user(self):
        User.objects.create_user(username='testuser', password='password123')
        data = {
            'username': 'testuser',
            'password': 'testpassword',
            'email': 'test@gmail.com'
        }
        response = self.client.post(self.url, data)
        self.assertIn('A user with that username already exists.', response.data['username'])

    def test_register_missing_required_fields(self):
        data = {
            'username': 'testuser',
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("This field is required.", response.data['password'])


class LoginAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('api-login')


        # Create a test user
        self.username = 'testuser'
        self.password = 'testpassword'
        self.user = User.objects.create_user(username=self.username, password=self.password)

    def test_login_valid_credentials(self):
        data = {
            'username': self.username,
            'password': self.password,
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

        token = response.data['token']
        self.assertTrue(token)

    def test_login_invalid_credentials(self):
        data = {
            'username': self.username,
            'password': 'incorrect_password',
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)
        self.assertEqual(response.data['non_field_errors'], ['Unable to log in with provided credentials.'])

    def test_login_missing_required_fields(self):
        data = {
            'username': self.username,
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)
        self.assertEqual(response.data['password'], ['This field is required.'])


class SearchBookAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('search-book')

        self.author1 = Author.objects.create(name='Test Author1')
        self.author2 = Author.objects.create(name='Test Author2')
        self.language1 = Language.objects.create(name='English')
        self.language2 = Language.objects.create(name='Vietnamese')
        self.genre1 = Genre.objects.create(name='Fiction')
        self.genre2 = Genre.objects.create(name='Drama')
        # Create some test books
        self.book1 = Book.objects.create(title='Book1', author=self.author1, language=self.language1, isbn='1234567890123')
        self.book1.genre.add(self.genre1)
        self.book2 = Book.objects.create(title='Book2', author=self.author2, language=self.language2, isbn='1234567890124')
        self.book2.genre.add(self.genre2)
        self.book3 = Book.objects.create(title='Book3', author=self.author1, language=self.language1, isbn='1234567890125')
        self.book3.genre.add(self.genre1)

    def test_search_by_title(self):
        query_params = {'title': 'Book1'}
        response = self.client.get(self.url, query_params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], str(self.book1.title))

    def test_search_by_author(self):
        query_params = {'author': '1'}
        response = self.client.get(self.url, query_params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['author'], 1)
        self.assertEqual(response.data[1]['author'], 1)

    def test_search_by_language(self):
        query_params = {'language': '1'}
        response = self.client.get(self.url, query_params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['language'], 1)
        self.assertEqual(response.data[1]['language'], 1)

    def test_search_by_genre(self):
        query_params = {'genre': '1'}

        response = self.client.get(self.url, query_params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_search_with_multiple_filters(self):
        query_params = {'author': '1', 'language': '1'}
        response = self.client.get(self.url, query_params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['author'], 1)
        self.assertEqual(response.data[0]['language'], 1)

class BorrowBookAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('borrow-book')

        author = Author.objects.create(name='Author 1')
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.book = Book.objects.create(
            title='Test Book',
            author=author,
            summary='Test Summary',
            isbn='1234567890123'
        )
        self.book.genre.add(Genre.objects.create(name='Test Genre'))
        self.book.save()
        self.book_copy = BookCopy.objects.create(
            book=self.book,
            status='a',
            publisher='Test Publisher'
        )

    def test_borrow_book(self):
        data = {
            'borrower': self.user.id,
            'book_copy': self.book_copy.id,
            'start_date': date.today(),
            'due_date': date.today()
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('borrow', response.data)

    def test_borrow_book_invalid_data(self):
        data = {
            'book_id': 999, 
            'borrower_id': self.user.id,
            'start_date':'2023-01-01',
            'due_date':'2023-05-02'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_borrow_book_missing_required_fields(self):
        data = {
            'book_id': 1, 
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['start_date'], ['This field is required.'])


class PendingBorrowingAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('pending-borrowing')  

        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.book = Book.objects.create(
            title='Test Book',
            summary='Test Summary',
            isbn='1234567890123'
        )
        self.book.genre.add(Genre.objects.create(name='Test Genre'))
        self.book.save()
        self.book_copy = BookCopy.objects.create(
            book=self.book,
            status='a',
            publisher='Test Publisher'
        )

        self.borrowing1 = Borrowing.objects.create(
            borrower=self.user,
            book_copy=self.book_copy,
            start_date='2023-01-01',
            due_date='2023-05-01',
            status='p'
        )
        self.borrowing2 = Borrowing.objects.create(
            borrower=self.user,
            book_copy=self.book_copy,
            start_date='2023-01-01',
            due_date='2023-05-02',
            status='r'
        )

    def test_get_pending_borrowings(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_pending_borrowings_no_results(self):
        # Set all borrowings to a non-pending status
        Borrowing.objects.update(status='a')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_get_pending_borrowings_with_different_status(self):
        borrowing3 = Borrowing.objects.create(
            borrower=self.user,
            book_copy=self.book_copy,
            start_date='2023-01-01',
            due_date='2023-05-02',
            status='d'
        )
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_pending_borrowings_serialized_data(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Additional assertions to verify the serialized data
        for borrowing_data in response.data:
            self.assertEqual(set(borrowing_data.keys()), {'book_copy', 'start_date',
                                        'borrower', 'status', 'due_date', 'decline_reason'})
            self.assertEqual(borrowing_data['status'], 'p')


class ProcessBorrowBookAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.book = Book.objects.create(
            title='Test Book',
            summary='Test Summary',
            isbn='1234567890123'
        )
        self.book.genre.add(Genre.objects.create(name='Test Genre'))
        self.book.save()
        self.book_copy = BookCopy.objects.create(
            book=self.book,
            status='a',
            publisher='Test Publisher'
        )

        self.borrowing = Borrowing.objects.create(
            borrower=self.user,
            book_copy=self.book_copy,
            start_date='2023-01-01',
            due_date='2023-05-01',
            status='p'
        )

    def test_update_borrowing_status(self):
        url = reverse('update-status', kwargs={'id': self.borrowing.id})
        data = {'status': 'a'}  # Set the status to 'a' (approved)
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_borrowing = Borrowing.objects.get(id=self.borrowing.id)
        self.assertEqual(updated_borrowing.status, 'a')

    def test_update_borrowing_status_invalid_id(self):
        url = reverse('update-status', kwargs={'id': 999})  # Provide a non-existing borrowing ID
        data = {'status': 'a'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_borrowing_status_invalid_status(self):
        url = reverse('update-status', kwargs={'id': self.borrowing.id})
        data = {'status': 'x'}  # Provide an invalid status
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('status', response.data)
        self.assertEqual(str(response.data['status']), '''[ErrorDetail(string='"x" is not a valid choice.', code='invalid_choice')]''')

    def test_get_borrowing_details(self):
        url = reverse('update-status', kwargs={'id': self.borrowing.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], self.borrowing.status)
