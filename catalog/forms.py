import datetime

from django import forms

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from .models import Book, Author, Review, Borrowing
from django.contrib.auth.models import User

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    phone_no = forms.CharField(max_length = 20)
    first_name = forms.CharField(max_length = 20)
    last_name = forms.CharField(max_length = 20)
    class Meta:
        model = User
        fields = ['username', 'email', 'phone_no', 'password1', 'password2']

class SearchAuthorForm(ModelForm):
    class Meta:
        model = Author
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super(SearchAuthorForm, self).__init__(*args, **kwargs)
        self.fields['name'].label = 'Author name'
        self.fields['name'].required = False

class SearchBookForm(ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'genre', 'language']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'author': forms.Select(attrs={'class': 'form-select'}),
            'genre': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'language': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        super(SearchBookForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].required = False

class ReviewBookForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['book', 'point', 'comment']
        widgets = {
            'book': forms.Select(attrs={'class': 'form-control'}),
            'point': forms.NumberInput(attrs={'class': 'form-control'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows':'5'}),
        }
    
    def __init__(self, *args, **kwargs):
        super(ReviewBookForm, self).__init__(*args, **kwargs)
        self.initial['book'] = kwargs['initial']['book_id']
        self.fields['book'].disabled = True

    def clean_point(self):
        data = self.cleaned_data['point']

        if data < 1:
            raise ValidationError(_('Invalid data - point cannot be smaller than 1'))
        if data > 5:
            raise ValidationError(_('Invalid point - point cannot larger than 5'))

        return data

class BorrowBookForm(forms.ModelForm):
    class Meta:
        model = Borrowing
        fields = ['book_copy', 'start_date', 'due_date']
        widgets = {
            'book_copy': forms.Select(attrs={'class': 'form-control'}),
            'start_date': forms.widgets.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'due_date': forms.widgets.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(BorrowBookForm, self).__init__(*args, **kwargs)
        self.initial['book_copy'] = kwargs['initial']['bookcopy_id']
        self.fields['book_copy'].disabled = True

    def clean_start_date(self):
        data = self.cleaned_data['start_date']
        if data < datetime.date.today():
            raise ValidationError(_('Invalid start date - start date cannot be in the past'))
        return data

    def clean_due_date(self):
        data = self.cleaned_data['due_date']
        if data < datetime.date.today():
            raise ValidationError(_('Invalid due date - due date cannot be in the past'))
        if data < self.cleaned_data['start_date']:
            raise ValidationError(_('Invalid due date - due date cannot be earlier than start date'))
        return data

class DeclineBorrowingForm(forms.ModelForm):

    class Meta:
        model = Borrowing
        fields = ['book_copy', 'borrower', 'start_date', 'due_date', 'decline_reason']
        widgets = {
            'book_copy': forms.Select(attrs={'class': 'form-control'}),
            'borrower': forms.TextInput(attrs={'class': 'form-control'}),
            'start_date': forms.widgets.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'due_date': forms.widgets.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'decline_reason': forms.Textarea(attrs={'class': 'form-control', 'rows':'5'}),
        }

    def __init__(self, *args, **kwargs):
        super(DeclineBorrowingForm, self).__init__(*args, **kwargs)
        initial = kwargs.get("initial")
        self.initial['book_copy'] = initial['bookcopy_id']
        self.initial['borrower'] = initial['borrower_id']
        self.fields['book_copy'].disabled = True
        self.fields['borrower'].disabled = True
        self.fields['start_date'].disabled = True
        self.fields['due_date'].disabled = True
        self.fields['decline_reason'].required = True
