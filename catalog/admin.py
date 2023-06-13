from django.contrib import admin
from .models import Author, Genre, Language, Book, Review, Borrowing, BookCopy

admin.site.register(Genre)
admin.site.register(Language)
admin.site.register(Review)

# Define the admin class
class BooksInline(admin.TabularInline):
    model = Book

class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name', 'date_of_birth', 'date_of_death')
    fields = ['name', ('date_of_birth', 'date_of_death')]
    inlines = [BooksInline]

# Register the admin class with the associated model
admin.site.register(Author, AuthorAdmin)

class BooksCopyInline(admin.TabularInline):
    model = BookCopy

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'display_genre')
    inlines = [BooksCopyInline]

# Register the Admin classes for BookCopy using the decorator
@admin.register(BookCopy)
class BookCopyAdmin(admin.ModelAdmin):
    list_display = ('book', 'status', 'published_date', 'id')
    list_filter = ('book', 'status')
    fieldsets = (
        (None, {
            'fields': ('book', 'publisher', 'published_date', 'id')
        }),
        ('Availability', {
            'fields': ('status',)
        }),
    )

@admin.register(Borrowing)
class BorrowingAdmin(admin.ModelAdmin):
    list_display = ('book_copy', 'borrower', 'start_date', 'due_date', 'status')
    fields = ['book_copy', 'borrower', ('start_date', 'due_date'), 'status', 'decline_reason']
