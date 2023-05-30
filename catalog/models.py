from django.db import models
from django.urls import reverse # Used to generate URLs by reversing the URL patterns
import uuid # Required for unique book copies
from django.contrib.auth.models import User
from datetime import date

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import Avg

class Genre(models.Model):
    """Model representing a book genre."""
    name = models.CharField(max_length=200, help_text='Enter a book genre (e.g. Science Fiction)')

    def __str__(self):
        """String for representing the Model object."""
        return self.name

class Language(models.Model):
    """Model representing a Language (e.g. English, French, Japanese, etc.)"""
    name = models.CharField(max_length=200,
                            help_text="Enter the book's natural language (e.g. English, French, Japanese etc.)")

    def __str__(self):
        """String for representing the Model object (in Admin site etc.)"""
        return self.name

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=False)
    book = models.ForeignKey('Book', on_delete=models.CASCADE)
    comment = models.TextField(max_length=500, help_text="Enter comment about the book", null=True, blank=True)
    point = models.IntegerField(
        default=5,
        validators=[
            MaxValueValidator(5),
            MinValueValidator(1)
        ],
        null=False,
        blank=False)
    created_at = models.DateTimeField(auto_now_add=True)

class Book(models.Model):
    """Model representing a book (but not a specific copy of a book)."""
    title = models.CharField(max_length=200)
    author = models.ForeignKey('Author', on_delete=models.SET_NULL, null=True)
    summary = models.TextField(max_length=1000, help_text='Enter a brief description of the book')
    isbn = models.CharField('ISBN', max_length=13, unique=True,
                            help_text='13 Character <a href="https://www.isbn-international.org/content/what-isbn">ISBN number</a>')
    genre = models.ManyToManyField(Genre, help_text='Select a genre for this book')
    language = models.ForeignKey('Language', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        """String for representing the Model object."""
        return self.title

    def get_absolute_url(self):
        """Returns the URL to access a detail record for this book."""
        return reverse('book-detail', args=[str(self.id)])

    def display_genre(self):
        """Create a string for the Genre. This is required to display genre in Admin."""
        return ', '.join(genre.name for genre in self.genre.all()[:3])

    display_genre.short_description = 'Genre'

    def get_average_rating(self):
        return (Review.objects.all()
            .filter(book=self)
            .aggregate(avg_rating=Avg('point'))
            .get('avg_rating', 0.00))
    
    def get_number_of_available_copies(self):
        return (BookCopy.objects
            .filter(book=self)
            .filter(status__exact='a')
            .count())

class Author(models.Model):
    """Model representing an author."""
    name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField('Died', null=True, blank=True)

    class Meta:
        ordering = ['name']

    def get_absolute_url(self):
        """Returns the URL to access a particular author instance."""
        return reverse('author-detail', args=[str(self.id)])

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.name}'

class BookCopy(models.Model):
    """Model representing a specific copy of a book (i.e. that can be borrowed from the library)."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text='Unique ID for this particular book across whole library')
    book = models.ForeignKey('Book', on_delete=models.RESTRICT, null=True)
    publisher = models.CharField(max_length=200)
    published_date = models.DateField(null=True, blank=True)

    STATUS = (
        ('m', 'Maintenance'),
        ('b', 'Borrowed'),
        ('a', 'Available'),
        ('r', 'Reserved'), # (reserved: borrowing request apporved, but book copy is not being borrowed yet)
    )

    status = models.CharField(
        max_length=1,
        choices=STATUS,
        blank=True,
        default='m',
        help_text='Book copy availability',
    )

    class Meta:
        ordering = ['book']

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.book.title} ({self.publisher}, {self.published_date})'

class Borrowing(models.Model):
    borrower = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=False)
    book_copy = models.ForeignKey(BookCopy, on_delete=models.RESTRICT)
    start_date = models.DateField(null=False, blank=False)
    due_date = models.DateField(null=False, blank=False)
    decline_reason = models.CharField(max_length=200, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    BORROWING_STATUS = (
        ('p', 'Pending'),
        ('c', 'Canceled'),
        ('a', 'Approved'),
        ('d', 'Declined'),
        ('b', 'Borrowing'),
        ('r', 'Returned'),
    )

    status = models.CharField(
        max_length=1,
        choices=BORROWING_STATUS,
        blank=False,
        default='p',
        help_text='Borrowing quest status',
    )

    class Meta:
        ordering = ['-updated_at']
        permissions = (
            ("can_view_all_borrowing", "Can view all borrowing requests"),
            ("can_approve_borrowing", "Can set borrowing request as approved"),
            ("can_decline_borrowing", "Can set borrowing request as declined"),
            ("can_mark_borrowing", "Can set borrowing request as borrowing"),
            ("can_mark_returned", "Can set borrowing request as returned"),
        )

    def __str__(self):
        return f'{self.book_copy.book} - borrowed by {self.borrower}'

    @property
    def is_overdue(self):
        return bool(date.today() > self.due_date) and (self.status != 'r')
        