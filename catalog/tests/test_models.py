from django.test import TestCase
from django.urls import reverse
from catalog.models import Author, Genre, Book, Language, Review, User, BookCopy, Borrowing
from datetime import date

class AuthorModelTest(TestCase):
    @classmethod
    def setUpTestData(self):
        self.author = Author.objects.create(
            name='Test Author',
            date_of_birth='2000-01-01',
            date_of_death='2022-05-05'
        )

    def test_author_str(self):
        self.assertEqual(str(self.author), 'Test Author')

    def test_author_absolute_url(self):
        expected_url = reverse('author-detail', args=[str(self.author.id)])
        self.assertEqual(self.author.get_absolute_url(), expected_url)

    def test_author_dates(self):
        self.assertEqual(self.author.date_of_birth, '2000-01-01')
        self.assertEqual(self.author.date_of_death, '2022-05-05')

    def test_name_label(self):
        author = Author.objects.get(id=1)
        field_label = author._meta.get_field('name').verbose_name
        self.assertEqual(field_label, 'name')

    def test_date_of_birth_label(self):
        author = Author.objects.get(id=1)
        field_label = author._meta.get_field('date_of_birth').verbose_name
        self.assertEqual(field_label, 'date of birth')

    def test_date_of_death_label(self):
        author = Author.objects.get(id=1)
        field_label = author._meta.get_field('date_of_death').verbose_name
        self.assertEqual(field_label, 'Died')

    def test_name_max_length(self):
        author = Author.objects.get(id=1)
        max_length = author._meta.get_field('name').max_length
        self.assertEqual(max_length, 100)

class GenreModelTest(TestCase):
    @classmethod
    def setUpTestData(self):
        self.genre = Genre.objects.create(name='Test Genre')

    def test_genre_str(self):
        self.assertEqual(str(self.genre), 'Test Genre')

    def test_name_label(self):
        genre = Genre.objects.get(id=1)
        field_label = genre._meta.get_field('name').verbose_name
        self.assertEqual(field_label, 'name')

    def test_name_max_length(self):
        genre = Genre.objects.get(id=1)
        max_length = genre._meta.get_field('name').max_length
        self.assertEqual(max_length, 200)

class LanguageModelTest(TestCase):
    @classmethod
    def setUpTestData(self):
        self.language = Language.objects.create(name='Test Language')
    
    def test_language_str(self):
        self.assertEqual(str(self.language), 'Test Language')
    
    def test_name_label(self):
        language = Language.objects.get(id=1)
        field_label = language._meta.get_field('name').verbose_name
        self.assertEqual(field_label, 'name')

    def test_name_max_length(self):
        language = Language.objects.get(id=1)
        max_length = language._meta.get_field('name').max_length
        self.assertEqual(max_length, 200)

class ReviewModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(username='testuser', password='testpassword')
        book = Book.objects.create(title='Test Book')
        Review.objects.create(
            user=user,
            book=book,
            comment='This book is great!',
            point=4
        )

    def test_review_user(self):
        review = Review.objects.get(id=1)
        user = User.objects.get(username='testuser')
        self.assertEqual(review.user, user)

    def test_review_book(self):
        review = Review.objects.get(id=1)
        book = Book.objects.get(title='Test Book')
        self.assertEqual(review.book, book)

    def test_review_comment(self):
        review = Review.objects.get(id=1)
        expected_comment = 'This book is great!'
        self.assertEqual(review.comment, expected_comment)

    def test_review_point(self):
        review = Review.objects.get(id=1)
        expected_point = 4
        self.assertEqual(review.point, expected_point)

    def test_review_created_at(self):
        review = Review.objects.get(id=1)
        self.assertIsNotNone(review.created_at)

    def test_review_point_validators(self):
        validators = [validator.__class__.__name__ for validator in Review._meta.get_field('point').validators]
        expected_validators = ['MaxValueValidator', 'MinValueValidator']
        self.assertEqual(validators, expected_validators)

    def test_review_point_max_value(self):
        review = Review.objects.get(id=1)
        self.assertEqual(review._meta.get_field('point').validators[0].limit_value, 5)

    def test_review_point_min_value(self):
        review = Review.objects.get(id=1)
        self.assertEqual(review._meta.get_field('point').validators[1].limit_value, 1)
    
class BookModelTest(TestCase):
    @classmethod
    def setUpTestData(self):
        self.book = Book.objects.create(
            title='Test Book',
            summary='Test Summary',
            isbn='1234567890123'
        )
        self.book.genre.add(Genre.objects.create(name='Test Genre'))
        self.book.language = Language.objects.create(name='Test Language')
        self.book.save()

    def test_book_str(self):
        self.assertEqual(str(self.book), 'Test Book')
    
    def test_book_absolute_url(self):
        expected_url = reverse('book-detail', args=[str(self.book.id)])
        self.assertEqual(self.book.get_absolute_url(), expected_url)
    
    def test_book_title(self):
        self.assertEqual(self.book.title, 'Test Book')
    
    def test_book_summary(self):
        self.assertEqual(self.book.summary, 'Test Summary')
    
    def test_book_isbn(self):
        self.assertEqual(self.book.isbn, '1234567890123')
    
    def test_book_genre(self):
        self.assertEqual(self.book.genre.all()[0].name, 'Test Genre')
    
    def test_book_language(self):
        self.assertEqual(self.book.language.name, 'Test Language')

    def test_book_title_label(self):
        book = Book.objects.get(id=1)
        field_label = book._meta.get_field('title').verbose_name
        self.assertEqual(field_label, 'title')
    
    def test_book_summary_label(self):
        book = Book.objects.get(id=1)
        field_label = book._meta.get_field('summary').verbose_name
        self.assertEqual(field_label, 'summary')
    
    def test_book_isbn_label(self):
        book = Book.objects.get(id=1)
        field_label = book._meta.get_field('isbn').verbose_name
        self.assertEqual(field_label, 'ISBN')
    
    def test_book_genre_label(self):
        book = Book.objects.get(id=1)
        field_label = book._meta.get_field('genre').verbose_name
        self.assertEqual(field_label, 'genre')
    
    def test_book_language_label(self):
        book = Book.objects.get(id=1)
        field_label = book._meta.get_field('language').verbose_name
        self.assertEqual(field_label, 'language')
    
    def test_book_title_max_length(self):
        book = Book.objects.get(id=1)
        max_length = book._meta.get_field('title').max_length
        self.assertEqual(max_length, 200)
    
    def test_book_isbn_max_length(self):
        book = Book.objects.get(id=1)
        max_length = book._meta.get_field('isbn').max_length
        self.assertEqual(max_length, 13)
    
    def test_book_display_genre(self):
        book = Book.objects.get(id=1)
        self.assertEqual(book.display_genre(), 'Test Genre')
    
    def test_book_get_average_rating(self):
        book = Book.objects.get(id=1)
        self.assertEqual(book.get_average_rating(), None)
    
    def test_book_get_number_of_available_copies(self):
        book = Book.objects.get(id=1)
        self.assertEqual(book.get_number_of_available_copies(), 0)

class BookCopyModelTest(TestCase):
    @classmethod
    def setUpTestData(self):
        self.book = Book.objects.create(
            title='Test Book',
            summary='Test Summary',
            isbn='1234567890123'
        )
        self.book.genre.add(Genre.objects.create(name='Test Genre'))
        self.book.language = Language.objects.create(name='Test Language')
        self.book.save()
        self.book_copy = BookCopy.objects.create(
            book=self.book,
            status='a',
            publisher='pub'
        )

    def test_book_copy_book(self):
        book_copy = BookCopy.objects.get(publisher='pub')
        self.assertEqual(book_copy.book, self.book)

    def test_book_copy_status(self):
        book_copy = self.book_copy
        self.assertEqual(book_copy.status, 'a')

    def test_book_copy_book_label(self):
        book_copy = self.book_copy
        field_label = book_copy._meta.get_field('book').verbose_name
        self.assertEqual(field_label, 'book')

    def test_book_copy_status_label(self):
        book_copy = self.book_copy
        field_label = book_copy._meta.get_field('status').verbose_name
        self.assertEqual(field_label, 'status')

    def test_book_copy_status_max_length(self):
        book_copy = self.book_copy
        max_length = book_copy._meta.get_field('status').max_length
        self.assertEqual(max_length, 1)
    
    def test_book_copy_get_status(self):
        book_copy = self.book_copy
        self.assertEqual(book_copy.status, 'a')

    def test_book_copy_get_status_borrowed(self):
        book_copy = BookCopy.objects.get(publisher='pub')
        book_copy.status = 'b'
        book_copy.save()
        self.assertEqual(book_copy.status, 'b')
    
    def test_book_copy_get_status_reserved(self):
        book_copy = BookCopy.objects.get(publisher='pub')
        book_copy.status = 'r'
        book_copy.save()
        self.assertEqual(book_copy.status, 'r')

    def test_book_copy_get_status_maintenance(self):
        book_copy = BookCopy.objects.get(publisher='pub')
        book_copy.status = 'm'
        book_copy.save()
        self.assertEqual(book_copy.status, 'm')

class BorrowingModelTest(TestCase):
    @classmethod
    def setUpTestData(self):
        self.book = Book.objects.create(
            title='Test Book',
            summary='Test Summary',
            isbn='1234567890123'
        )
        self.book.genre.add(Genre.objects.create(name='Test Genre'))
        self.book.language = Language.objects.create(name='Test Language')
        self.book.save()
        self.book_copy = BookCopy.objects.create(
            book=self.book,
            status='a',
            publisher='Test Publisher'
        )
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        Borrowing.objects.create(
            borrower=self.user,
            book_copy=self.book_copy,
            start_date='2023-01-01',
            due_date='2023-05-01',
            status='b'
        )

    def test_borrowing_borrower(self):
        borrowing = Borrowing.objects.get(status='b')
        user = User.objects.get(username='testuser')
        self.assertEqual(borrowing.borrower, user)

    def test_borrowing_book_copy(self):
        borrowing = Borrowing.objects.get(status='b')
        book_copy = BookCopy.objects.get(publisher='Test Publisher')
        self.assertEqual(borrowing.book_copy, book_copy)

    def test_borrowing_start_date(self):
        borrowing = Borrowing.objects.get(status='b')
        expected_start_date = '2023-01-01'
        self.assertEqual(str(borrowing.start_date), expected_start_date)

    def test_borrowing_due_date(self):
        borrowing = Borrowing.objects.get(status='b')
        expected_due_date = '2023-05-01'
        self.assertEqual(str(borrowing.due_date), expected_due_date)

    def test_borrowing_decline_reason(self):
        borrowing = Borrowing.objects.get(status='b')
        self.assertIsNone(borrowing.decline_reason)

    def test_borrowing_updated_at(self):
        borrowing = Borrowing.objects.get(status='b')
        self.assertIsNotNone(borrowing.updated_at)

    def test_borrowing_status_choices(self):
        borrowing = Borrowing.objects.get(status='b')
        status_choices = [choice[0] for choice in Borrowing.BORROWING_STATUS]
        self.assertIn(borrowing.status, status_choices)

    def test_borrowing_str(self):
        borrowing = Borrowing.objects.get(status='b')
        expected_str = 'Test Book - borrowed by testuser'
        self.assertEqual(str(borrowing), expected_str)

    def test_borrowing_ordering(self):
        borrowings = Borrowing.objects.all()
        borrowings = [str(borrowing) for borrowing in borrowings]
        self.assertQuerysetEqual(borrowings, ['Test Book - borrowed by testuser'])

    def test_borrowing_is_overdue_true(self):
        borrowing = Borrowing.objects.get(status='b')
        borrowing.due_date = date(2023, 1, 1)
        borrowing.save()
        self.assertTrue(borrowing.is_overdue)

    def test_borrowing_is_overdue_false(self):
        borrowing = Borrowing.objects.get(status='b')
        borrowing.due_date = date(2024, 6, 13)
        borrowing.save()
        self.assertFalse(borrowing.is_overdue)
