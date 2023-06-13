from django.shortcuts import render
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from .models import Book, Author, Genre, Borrowing, BookCopy

import datetime

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse

from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from catalog.forms import SearchAuthorForm, SearchBookForm, ReviewBookForm, BorrowBookForm, DeclineBorrowingForm

from django.db.models import Avg
from django.views.generic.edit import FormMixin
from django.contrib import messages

from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm

from .forms import UserRegisterForm
from django.conf import settings
import smtplib

# view file index:
# 1. INDEX
# 2. BOOK
# 3. AUTHOR
# 4. REVIEW BOOK
# 5. BORROWING BOOK

############  1. INDEX + LOGIN + REGISTER  ############

def index(request):
    """View function for home page of site."""

    num_books = Book.objects.all().count()
    num_copies = BookCopy.objects.all().count()
    num_genres = Genre.objects.all().count()
    num_copies_available = BookCopy.objects.filter(status__exact='a').count()
    num_authors = Author.objects.count()
    top_rated_books = Book.objects.annotate(avg_rating=Avg('review__point')).order_by('-avg_rating')[:10]

    context = {
        'num_books': num_books,
        'num_copies': num_copies,
        'num_copies_available': num_copies_available,
        'num_authors': num_authors,
        'num_genres': num_genres,
        'top_rated_books': top_rated_books,
    }

    return render(request, 'index.html', context=context)

def Register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            ######################### mail system ####################################
            email_server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
            email_server.starttls()
            email_server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            subject = 'Account created successfully!!!'
            message = 'Welcome\n\nYour account has been created ! You are now able to log in'
            content = f'Subject: {subject}\n\n{message}.\n\nLogin here: http://127.0.0.1:8000/login/'
            to = [email]
            email_server.sendmail(settings.EMAIL_HOST_USER, to, content)
            email_server.quit()
            ##################################################################
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'user/register.html', {'form': form, 'title':'register here'})


def Login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username = username, password = password)
        if user is not None:
            form = login(request, user)
            messages.success(request, f' welcome {username} !!')
            return redirect('index')
        else:
            messages.info(request, f'account done not exit plz sign in')
    form = AuthenticationForm()
    return render(request, 'user/login.html', {'form':form, 'title':'log in'})

############  2. BOOK  ############

class BookListView(generic.ListView, FormMixin):
    """Generic class-based view for a list of books."""
    model = Book
    paginate_by = 10
    form_class = SearchBookForm

    def get_queryset(self):
        form = SearchBookForm(self.request.GET)

        if form.is_valid():
            title = form.cleaned_data['title']
            author = form.cleaned_data['author']
            genre = form.cleaned_data['genre']
            language = form.cleaned_data['language']

            book_list = self.model.objects.filter(title__icontains=title)
            if author:
                book_list = book_list.filter(author__name__icontains=author)
            if genre:
                book_list = book_list.filter(genre__in=genre)
            if language:
                book_list = book_list.filter(language__name__iexact=language)

            return book_list.distinct()

        return self.model.objects.all()

class BookDetailView(generic.DetailView):
    """Generic class-based detail view for a book."""
    model = Book

class BookCreate(CreateView):
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language']
    permission_required = 'catalog.can_mark_returned'

class BookUpdate(UpdateView):
    model = Book
    fields = '__all__' # Not recommended (potential security issue if more fields added)
    permission_required = 'catalog.can_mark_returned'

class BookDelete(DeleteView):
    model = Book
    success_url = reverse_lazy('authors')
    permission_required = 'catalog.can_mark_returned'


############  3. AUTHOR  ############

class AuthorListView(generic.ListView, FormMixin):
    """Generic class-based list view for a list of authors."""
    model = Author
    paginate_by = 10
    form_class = SearchAuthorForm

    def get_queryset(self):
        form = SearchAuthorForm(self.request.GET)

        if form.is_valid():
            name = form.cleaned_data['name']
            return self.model.objects.filter(name__icontains=name)

        return self.model.objects.all()

class AuthorDetailView(generic.DetailView):
    """Generic class-based detail view for an author."""
    model = Author

class AuthorCreate(CreateView):
    model = Author
    fields = ['name', 'date_of_birth', 'date_of_death']
    permission_required = 'catalog.can_mark_returned'

class AuthorUpdate(UpdateView):
    model = Author
    fields = '__all__'
    permission_required = 'catalog.can_mark_returned'

class AuthorDelete(DeleteView):
    model = Author
    success_url = reverse_lazy('authors')
    permission_required = 'catalog.can_mark_returned'


############  4. REVIEW BOOK  ############

def review_book(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    initial_dict = {
        'book_id' : book_id,
    }

    if request.method == 'POST':
        form = ReviewBookForm(request.POST, initial = initial_dict)

        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.book = book
            review.save()
            return HttpResponseRedirect(reverse('book-detail', args=(book.id,)))

    else:
        form = ReviewBookForm(initial = initial_dict)
        

    context = {
        'form': form,
        'form_title': 'Write Review',
    }

    return render(request, 'form_generic.html', context)


############  5. BORROW BOOK  ############
# borrowing status change:
#     pending -> canceled -> approvde/declined -> borrowing -> returned
#     (user)     (user)      (staff)              (staff)      (staff)

# book copy status change
#     available -> reserved -> borrowed -> available

class BorrowingByUserListView(LoginRequiredMixin, generic.ListView):
    model = Borrowing
    template_name = 'catalog/borrowing_list_user.html'
    paginate_by = 10

    def get_queryset(self):
        return Borrowing.objects.filter(borrower=self.request.user).order_by('-updated_at')

class BorrowingByStaffListView(LoginRequiredMixin, PermissionRequiredMixin, generic.ListView):
    model = Borrowing
    template_name = 'catalog/borrowing_list_staff.html'
    permission_required = 'catalog.can_view_all_borrowing'
    paginate_by = 10

    def get_queryset(self):
        return Borrowing.objects.all()

def borrow_book(request, book_id, bookcopy_id):
    book = get_object_or_404(Book, pk=book_id)
    bookcopy = get_object_or_404(BookCopy, pk=bookcopy_id)

    initial_dict = {
        'bookcopy_id' : bookcopy_id,
        'start_date': datetime.date.today,
        'due_date': datetime.date.today,
    }

    if request.method == 'POST':
        form = BorrowBookForm(request.POST, initial = initial_dict)

        if form.is_valid():
            borrowing = form.save(commit=False)
            borrowing.borrower = request.user
            borrowing.bookcopy = bookcopy
            borrowing.save()
            return HttpResponseRedirect(reverse('book-detail', args=(book.id,)))

    else:
        form = BorrowBookForm(initial = initial_dict)

    context = {
        'form': form,
        'form_title': 'Make Borrowing Request'
    }
    return render(request, 'form_generic.html', context)

def cancel_borrowing(request, pk):
    borrowing = get_object_or_404(Borrowing, pk=pk)

    if request.method == 'POST':
        borrowing.status = 'c' # canceled
        borrowing.save()

    return HttpResponseRedirect(reverse('borrowing-list'))

def approve_borrowing(request, pk):
    borrowing = get_object_or_404(Borrowing, pk=pk)
    book_copy = get_object_or_404(BookCopy, pk=borrowing.book_copy.id)

    if request.method == 'POST':
        if book_copy.status == 'a': # available
            borrowing.status = 'a' # approved
            borrowing.save()

            book_copy.status = 'r' # reserved
            book_copy.save()
            # send email to user
            ######################### mail system ####################################
            email_server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
            email_server.starttls()
            email_server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            subject = 'Borrowed success!!!'
            message = 'You have borrowed a book successfully'
            content = f'Subject: {subject}\n\n{message}. Book name: {book_copy.book.title}'
            to = [borrowing.borrower.email]
            email_server.sendmail(settings.EMAIL_HOST_USER, to, content)
            email_server.quit()
            ##################################################################
        else:
            messages.info(request, 'Cannot approve this request because the book copy is not available!')

    return HttpResponseRedirect(reverse('all-borrowing'))

def decline_borrowing(request, pk):
    borrowing = get_object_or_404(Borrowing, pk=pk)

    initial_dict = {
        'bookcopy_id' : borrowing.book_copy.id,
        'borrower_id': borrowing.borrower.id,
        'start_date': borrowing.start_date,
        'due_date': borrowing.due_date,
    }

    if request.method == 'POST':
        form = DeclineBorrowingForm(request.POST, initial = initial_dict)
        if form.is_valid():
            borrowing = form.save(commit=False)
            borrowing.status = 'd' # declined
            borrowing.save()
            ######################### mail system ####################################
            email_server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
            email_server.starttls()
            email_server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            subject = 'Borrowed failed!!!'
            message = 'You cant borrowed a book'
            # get declined reason
            declined_reason = form.cleaned_data['decline_reason']
            content = f'Subject: {subject}\n\n{message}.\n\nReason: {declined_reason}'
            to = [borrowing.borrower.email]
            email_server.sendmail(settings.EMAIL_HOST_USER, to, content)
            email_server.quit()
            ##################################################################
            return HttpResponseRedirect(reverse('all-borrowing'))

    else:
        form = DeclineBorrowingForm(initial = initial_dict)

    context = {
        'form': form,
        'form_title': 'Decline Borrowing Request'
    }
    return render(request, 'form_generic.html', context)

def start_borrowing(request, pk):
    borrowing = get_object_or_404(Borrowing, pk=pk)
    book_copy = get_object_or_404(BookCopy, pk=borrowing.book_copy.id)

    if request.method == 'POST':
        borrowing.status = 'b' # borrowing
        borrowing.save()

        book_copy.status = 'b' # borrowed
        book_copy.save()

    return HttpResponseRedirect(reverse('all-borrowing'))

def end_borrowing(request, pk):
    borrowing = get_object_or_404(Borrowing, pk=pk)
    book_copy = get_object_or_404(BookCopy, pk=borrowing.book_copy.id)

    if request.method == 'POST':
        borrowing.status = 'r' # returned
        borrowing.save()
        
        book_copy.status = 'a' # availabel
        book_copy.save()

    return HttpResponseRedirect(reverse('all-borrowing'))

def request_return_book(request, pk):
    borrowing = get_object_or_404(Borrowing, pk=pk)
    if request.method == 'POST':
        ######################### mail system ####################################
        email_server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
        email_server.starttls()
        email_server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        subject = 'Overdue borrowing book!!!'
        message = 'You must return a book because of due date'
        content = f'Subject: {subject}\n\n{message}.\n\nReturn Date: {borrowing.due_date}\n\nToday: {datetime.date.today()}'
        to = [borrowing.borrower.email]
        email_server.sendmail(settings.EMAIL_HOST_USER, to, content)
        email_server.quit()
        ##################################################################

    return HttpResponseRedirect(reverse('all-borrowing'))
    