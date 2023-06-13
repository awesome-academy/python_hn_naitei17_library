from django.test import TestCase, Client
from django.contrib.auth.models import User, Permission
from django.urls import reverse
from django.core.paginator import Page

from catalog.models import Book, Author, Genre, Review, Borrowing, BookCopy
from catalog.forms import ReviewBookForm
from datetime import date
from unittest.mock import patch

from django.conf import settings

class IndexViewTest(TestCase):
    def test_index_view(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

class RegisterViewTest(TestCase):
    def test_register_view(self):
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'testpassword',
            'password2': 'testpassword',
            'phone_no': '0123456789',
            'first_name': 'Test',
            'last_name': 'User',
        }
        response = self.client.post(reverse('register'), data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))

class LoginViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_login_view_with_valid_credentials(self):
        data = {
            'username': 'testuser',
            'password': 'testpassword',
        }
        response = self.client.post(reverse('login'), data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('index'))

    def test_login_view_with_invalid_credentials(self):
        data = {
            'username': 'testuser',
            'password': 'wrongpassword',
        }
        response = self.client.post(reverse('login'), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user/login.html')

class BookListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        author1 = Author.objects.create(name='Author 1')
        author2 = Author.objects.create(name='Author 2')

        # Create test genres
        genre1 = Genre.objects.create(name='Genre 1')
        genre2 = Genre.objects.create(name='Genre 2')

        # Create test books
        book1 = Book.objects.create(title='Book 1', author=author1, isbn = '1234567890123')
        book1.genre.add(genre1)
        book2 = Book.objects.create(title='Book 2', author=author2, isbn = '1234567890124')
        book2.genre.add(genre2)
        book3 = Book.objects.create(title='Book 3', author=author1, isbn = '1234567890125')
        book3.genre.add(genre1, genre2)
    
    def test_view_url_exists_at_desired_location(self):
        response = self.client.get(reverse('books'))
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('books'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('books'))
        self.assertTemplateUsed(response, 'catalog/book_list.html')  

    def test_pagination_is_ten(self):
        response = self.client.get(reverse('books'))
        self.assertIsInstance(response.context['page_obj'], Page)
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_search_book(self):
        data = {
            'title': 'Harry Potter',
            'author': 'J.K. Rowling',
            'genre': 'Fantasy',
            'language': 'English',
        }
        response = self.client.get(reverse('books'), data)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['page_obj'], Page)
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_invalid_search_book(self):
        data = {
            'title': 'Nonexistent Book',
            'author': 'Unknown Author',
            'genre': 'Nonexistent Genre',
            'language': 'Nonexistent Language',
        }
        response = self.client.get(reverse('books'), data)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['page_obj'], Page)
        self.assertEqual(len(response.context['page_obj']), 3)


class BookDetailViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        author = Author.objects.create(name='Author 1')
        genre = Genre.objects.create(name='Genre 1')
        book = Book.objects.create(title='Book 1', author=author, isbn='1234567890123')
        book.genre.add(genre)

    def test_book_detail_view(self):
        book = Book.objects.get(title='Book 1')
        response = self.client.get(reverse('book-detail', args=[book.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/book_detail.html')

class BookCreateViewTest(TestCase):
    def test_book_create_view(self):
        response = self.client.get(reverse('book-create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/book_form.html')

class BookUpdateViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        author = Author.objects.create(name='Author 1')
        genre = Genre.objects.create(name='Genre 1')
        book = Book.objects.create(title='Book 1', author=author, isbn='1234567890123')
        book.genre.add(genre)

    def test_book_update_view(self):
        book = Book.objects.get(title='Book 1')
        response = self.client.get(reverse('book-update', args=[book.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/book_form.html')

class BookDeleteViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        author = Author.objects.create(name='Author 1')
        genre = Genre.objects.create(name='Genre 1')
        book = Book.objects.create(title='Book 1', author=author)
        book.genre.add(genre)

    def test_book_delete_view(self):
        book = Book.objects.get(title='Book 1')
        response = self.client.post(reverse('book-delete', args=[book.id]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('authors'))

class AuthorListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create 13 authors for pagination tests
        number_of_authors = 13

        for author_id in range(number_of_authors):
            Author.objects.create(name=f'author {author_id}')

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/catalog/authors/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('authors'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('authors'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/author_list.html')

    def test_pagination_is_ten(self):
        response = self.client.get(reverse('authors'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] == True)
        self.assertEqual(len(response.context['author_list']), 10)

    def test_lists_all_authors(self):
        # Get second page and confirm it has (exactly) remaining 3 items
        response = self.client.get(reverse('authors')+'?page=2')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] == True)
        self.assertEqual(len(response.context['author_list']), 3)

class AuthorDetailViewTest(TestCase):
    def test_author_detail_view(self):
        author = Author.objects.create(
            name='J.K. Rowling',
            date_of_birth='1965-07-31',
            date_of_death=None,
        )
        response = self.client.get(reverse('author-detail', kwargs={'pk': author.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['author'], author)
        self.assertTemplateUsed(response, 'catalog/author_detail.html')

class AuthorCreateViewTest(TestCase):

    def test_author_create_view(self):
        response = self.client.get(reverse('author-create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/author_form.html')

        data = {
            'name': 'J.R.R. Tolkien',
            'date_of_birth': '1892-01-03',
            'date_of_death': '1973-09-02',
        }
        response = self.client.post(reverse('author-create'), data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('author-detail', kwargs={'pk': 1}))

class AuthorUpdateViewTest(TestCase):

    def test_author_update_view(self):
        author = Author.objects.create(
            name='J.K. Rowling',
            date_of_birth='1965-07-31',
            date_of_death=None,
        )
        response = self.client.get(reverse('author-update', kwargs={'pk': author.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/author_form.html')

        data = {
            'name': 'Joanne Rowling',
            'date_of_birth': '1965-07-31',
            'date_of_death': '',
        }
        response = self.client.post(reverse('author-update', kwargs={'pk': author.pk}), data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('author-detail', kwargs={'pk': author.pk}))

class AuthorDeleteViewTest(TestCase):

    def test_author_delete_view(self):
        author = Author.objects.create(
            name='J.K. Rowling',
            date_of_birth='1965-07-31',
            date_of_death=None,
        )
        response = self.client.get(reverse('author-delete', kwargs={'pk': author.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/author_confirm_delete.html')

        response = self.client.post(reverse('author-delete', kwargs={'pk': author.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('authors'))

class ReviewBookViewTest(TestCase):
    @classmethod
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.author = Author.objects.create(name='Test Author')
        self.book = Book.objects.create(title='Test Book', author=self.author, isbn='1234567890123')
        self.url = reverse('review-create', kwargs={'book_id': self.book.id})

    def test_review_book_view_get(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'form_generic.html')
        self.assertIsInstance(response.context['form'], ReviewBookForm)
        self.assertEqual(response.context['form_title'], 'Write Review')

    def test_review_book_view_post(self):
        self.client.force_login(self.user)
        form_data = {
            'point': 5,
            'comment': 'Great book!',
        }
        response = self.client.post(self.url, data=form_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('book-detail', kwargs={'pk': self.book.id}))

        review = Review.objects.get(book=self.book, user=self.user)
        self.assertEqual(review.point, form_data['point'])
        self.assertEqual(review.comment, form_data['comment'])

    def test_review_book_view_post_invalid_form(self):
        self.client.force_login(self.user)
        form_data = {
            'point': 6, 
            'comment': 'Great book!',
        }
        response = self.client.post(self.url, data=form_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'form_generic.html')
        self.assertIsInstance(response.context['form'], ReviewBookForm)
        self.assertEqual(response.context['form_title'], 'Write Review')
        self.assertFormError(response, 'form', 'point', 'Invalid point - point cannot larger than 5')

class BorrowingByUserListViewTest(TestCase):
    @classmethod
    def setUp(self):
        self.client = Client()
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
            status='b'
        )
        self.borrowing2 = Borrowing.objects.create(
            borrower=self.user,
            book_copy=self.book_copy,
            start_date='2023-01-01',
            due_date='2023-05-02',
            status='r'
        )
        self.borrowing3 = Borrowing.objects.create(
            borrower=self.user,
            book_copy=self.book_copy,
            start_date='2023-01-01',
            due_date='2023-05-03',
            status='b'
        )

        self.url = reverse('borrowing-list')

    def test_borrowing_by_user_list_view_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/borrowing_list_user.html')
        self.assertContains(response, self.borrowing1.status)
        self.assertContains(response, self.borrowing2.status)
        self.assertContains(response, self.borrowing3.status)

    def test_borrowing_by_user_list_view_pagination(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue('page_obj' in response.context)
        self.assertEqual(len(response.context['page_obj']), 3) 


class BorrowingByStaffListViewTest(TestCase):
    @classmethod
    def setUp(self):
        self.client = Client()
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
            status='b'
        )
        self.borrowing2 = Borrowing.objects.create(
            borrower=self.user,
            book_copy=self.book_copy,
            start_date='2023-01-01',
            due_date='2023-05-02',
            status='r'
        )
        self.borrowing3 = Borrowing.objects.create(
            borrower=self.user,
            book_copy=self.book_copy,
            start_date='2023-01-01',
            due_date='2023-05-03',
            status='b'
        )

        self.staff_user = User.objects.create_user(username='staffuser', password='testpassword')
        self.staff_user.user_permissions.add(Permission.objects.get(codename='can_view_all_borrowing'))
        self.url = reverse('all-borrowing')

    def test_borrowing_by_staff_list_view_without_permission(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_borrowing_by_staff_list_view_with_permission(self):
        self.client.force_login(self.staff_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/borrowing_list_staff.html')
        self.assertContains(response, self.borrowing1.status)
        self.assertContains(response, self.borrowing2.status)
        self.assertContains(response, self.borrowing3.status)

    def test_borrowing_by_staff_list_view_pagination(self):
        self.client.force_login(self.staff_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue('page_obj' in response.context)
        self.assertEqual(len(response.context['page_obj']), 3)

class BorrowBookViewTest(TestCase):
    @classmethod
    def setUp(self):
        self.client = Client()
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
        self.url = reverse('borrowing-create', args=(self.book.id, self.book_copy.id))

    def test_borrow_book_view_get_request(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'form_generic.html')
        self.assertIn('form', response.context)

class ApproveBorrowingViewTest(TestCase):
    @classmethod
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser',
                        password='testpassword', email='test@gmail.com')
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
        self.borrowing.save()
        self.url = reverse('borrowing-approve', args=(self.borrowing.id,))

    def test_approve_borrowing_view_get_request(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    @patch('catalog.views.smtplib.SMTP')
    def test_approve_borrowing_view_post_request_with_available_book_copy(self, mock_smtp):
        self.client.force_login(self.user)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        self.borrowing.refresh_from_db()
        self.book_copy.refresh_from_db()
        self.assertEqual(self.borrowing.status, 'a')
        self.assertEqual(self.book_copy.status, 'r')

        mock_email_server = mock_smtp.return_value
        mock_email_server.starttls.assert_called_once()
        mock_email_server.login.assert_called_once_with(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        mock_email_server.sendmail.assert_called_once()
        # Assert email content
        sent_email_content = mock_email_server.sendmail.call_args[0][2]
        self.assertIn('Borrowed success!!!', sent_email_content)
        self.assertIn('You have borrowed a book successfully', sent_email_content)
        self.assertIn(f'Book name: {self.book_copy.book.title}', sent_email_content)
        mock_email_server.quit.assert_called_once()

    def test_approve_borrowing_view_post_request_with_unavailable_book_copy(self):
        self.client.force_login(self.user)
        self.book_copy.status = 'r' 
        self.book_copy.save()
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        self.borrowing.refresh_from_db()
        self.book_copy.refresh_from_db()
        self.assertEqual(self.borrowing.status, 'p')
        self.assertEqual(self.book_copy.status, 'r')

class DeclineBorrowingViewTest(TestCase):
    @classmethod
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser',
                        password='testpassword', email='test@gmail.com')
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
        self.borrowing.save()
        self.url = reverse('borrowing-decline', args=(self.borrowing.id,))

    def test_decline_borrowing_view_get_request(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    @patch('catalog.views.smtplib.SMTP')
    def test_decline_borrowing_view_post_request(self, mock_smtp):
        self.client.force_login(self.user)
        response = self.client.post(self.url, {'decline_reason': 'Book not available'})
        self.assertEqual(response.status_code, 302)
        self.borrowing.refresh_from_db()
        self.borrowing.status = 'd'
        self.assertEqual(self.borrowing.status, 'd')

        mock_email_server = mock_smtp.return_value
        mock_email_server.starttls.assert_called_once()
        mock_email_server.login.assert_called_once_with(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        mock_email_server.sendmail.assert_called_once()
        # Assert email content
        sent_email_content = mock_email_server.sendmail.call_args[0][2]
        self.assertIn('Borrowed failed!!!', sent_email_content)
        self.assertIn('You cant borrowed a book', sent_email_content)
        self.assertIn('Reason: Book not available', sent_email_content)
        mock_email_server.quit.assert_called_once()

class StartBorrowingViewTest(TestCase):
    @classmethod
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser',
                        password='testpassword', email='test@gmail.com')
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
            status='a'
        )
        self.borrowing.save()
        self.url = reverse('borrowing-start', args=(self.borrowing.id,))

    def test_start_borrowing_view_get_request(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_start_borrowing_view_post_request(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        self.borrowing.refresh_from_db()
        self.assertEqual(self.borrowing.status, 'b')
        self.book_copy.refresh_from_db()
        self.assertEqual(self.book_copy.status, 'b')

class EndBorrowingViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser',
                        password='testpassword', email='test@gmail.com')
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
            status='b'
        )
        self.borrowing.save()
        self.url = reverse('borrowing-end', args=(self.borrowing.id,))

    def test_end_borrowing_view_get_request(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302) 

    def test_end_borrowing_view_post_request(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        self.borrowing.refresh_from_db()
        self.assertEqual(self.borrowing.status, 'r')
        self.book_copy.refresh_from_db()
        self.assertEqual(self.book_copy.status, 'a')

class RequestReturnBookViewTest(TestCase):
    @classmethod
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser',
                        password='testpassword', email='test@gmail.com')
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
            status='b'
        )
        self.borrowing.save()
        self.url = reverse('borrowing-request-return', args=(self.borrowing.id,))

    def test_request_return_book_view_get_request(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    @patch('catalog.views.smtplib.SMTP')
    def test_request_return_book_view_post_request(self, mock_smtp):
        mock_email_server = mock_smtp.return_value
        self.client.force_login(self.user)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)

        # Assert email server is called with the expected arguments
        mock_email_server.starttls.assert_called_once()
        mock_email_server.login.assert_called_once_with(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        mock_email_server.sendmail.assert_called_once()
        # Assert email content
        sent_email_content = mock_email_server.sendmail.call_args[0][2]
        self.assertIn('Overdue borrowing book!!!', sent_email_content)
        self.assertIn(str(self.borrowing.due_date), sent_email_content)
        self.assertIn(str(date.today()), sent_email_content)
        mock_email_server.quit.assert_called_once()
