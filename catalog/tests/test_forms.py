from django.test import TestCase
from django.core.exceptions import ValidationError

import datetime
from catalog.forms import UserRegisterForm, SearchAuthorForm, \
                        SearchBookForm, ReviewBookForm, BorrowBookForm, \
                        DeclineBorrowingForm

#####################################################################
class UserRegisterFormTest(TestCase):
    def test_valid_form_submission(self):
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'phone_no': '1234567890',
            'first_name': 'Cao',
            'last_name': 'Hieu',
            'password1': 'testpassword',
            'password2': 'testpassword'
        }
        form = UserRegisterForm(data=form_data)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')

    def test_invalid_form_submission(self):
        form_data = {
            'username': '',
            'email': 'invalid_email',
            'phone_no': '123456789012345678901',  # exceeds max length
            'first_name': '',
            'last_name': '',
            'password1': 'testpassword',
            'password2': 'differentpassword'
        }
        form = UserRegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertGreater(len(form.errors), 0)
        self.assertIn('username', form.errors)
        self.assertIn('email', form.errors)
        self.assertIn('phone_no', form.errors)
        self.assertIn('first_name', form.errors)
        self.assertIn('last_name', form.errors)
        self.assertIn('password2', form.errors)

    def test_password_mismatch(self):
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'phone_no': '1234567890',
            'first_name': 'Cao',
            'last_name': 'Hieu',
            'password1': 'testpassword',
            'password2': 'differentpassword'
        }
        form = UserRegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_email_field_validation(self):
        form_data = {
            'username': 'testuser',
            'email': 'invalid_email',
            'phone_no': '1234567890',
            'first_name': 'Cao',
            'last_name': 'Hieu',
            'password1': 'testpassword',
            'password2': 'testpassword'
        }
        form = UserRegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_max_length_validation(self):
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'phone_no': '123456789012345678901',  # exceeds max length
            'first_name': 'Cao',
            'last_name': 'hieu',
            'password1': 'testpassword',
            'password2': 'testpassword'
        }
        form = UserRegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('phone_no', form.errors)

    def test_required_field_validation(self):
        form_data = {
            'username': '',
            'email': '',
            'phone_no': '',
            'first_name': '',
            'last_name': '',
            'password1': '',
            'password2': ''
        }
        form = UserRegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        self.assertIn('email', form.errors)
        self.assertIn('password1', form.errors)
        self.assertIn('password2', form.errors)

#####################################################################
class SearchAuthorFormTest(TestCase):
    def test_valid_form_submission(self):
        form_data = {
            'name': 'cao'
        }
        form = SearchAuthorForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_widget_attrs(self):
        form = SearchAuthorForm()
        name_field = form.fields['name']
        self.assertEqual(name_field.widget.attrs.get('class'), 'form-control')

    def test_form_label(self):
        form = SearchAuthorForm()
        name_field = form.fields['name']
        self.assertEqual(name_field.label, 'Author name')

    def test_form_required(self):
        form = SearchAuthorForm()
        name_field = form.fields['name']
        self.assertFalse(name_field.required)

#####################################################################
class SearchBookFormTest(TestCase):
    def test_form_required_fields(self):
        form = SearchBookForm()
        self.assertFalse(form.fields['title'].required)
        self.assertFalse(form.fields['author'].required)
        self.assertFalse(form.fields['genre'].required)
        self.assertFalse(form.fields['language'].required)

    def test_empty_form_submission(self):
        form = SearchBookForm(data={})
        self.assertTrue(form.is_valid())

#####################################################################
class ReviewBookFormTest(TestCase):
    def test_form_initial_data(self):
        initial = {'book_id': 1}
        form = ReviewBookForm(initial=initial)
        self.assertEqual(form.initial['book'], 1)
        self.assertTrue(form.fields['book'].disabled)

    def test_invalid_form_point_upper_submission(self):
        book_id = 1
        form_data = {
            'book': book_id,
            'point': 6,  # Invalid point value
            'comment': ''
        }
        form = ReviewBookForm(data=form_data, initial={'book_id': book_id})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 2)
        self.assertIn('point', form.errors)

    def test_invalid_form_point_lower_submission(self):
        book_id = 1
        form_data = {
            'book': book_id,
            'point': 0,  # Invalid point value
            'comment': ''
        }
        form = ReviewBookForm(data=form_data, initial={'book_id': book_id})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 2)
        self.assertIn('point', form.errors)


#####################################################################
class BorrowBookFormTest(TestCase):
    def test_borrow_book_form_invalid_due_date(self):
        book_copy_id = 1
        start_date = datetime.date.today()
        due_date = datetime.date.today() - datetime.timedelta(days=1)

        form_data = {
            'book_copy': book_copy_id,
            'start_date': start_date,
            'due_date': due_date
        }
        form = BorrowBookForm(data=form_data, initial={'bookcopy_id': book_copy_id})

        self.assertFalse(form.is_valid())
        self.assertIn('due_date', form.errors)
        self.assertEqual(form.errors['due_date'][0], 'Invalid due date - due date cannot be in the past')

    def test_borrow_book_form_invalid_due_date_earlier_than_start_date(self):
        book_copy_id = 1
        start_date = datetime.date.today()
        due_date = start_date - datetime.timedelta(days=1)

        form_data = {
            'book_copy': book_copy_id,
            'start_date': start_date,
            'due_date': due_date
        }
        form = BorrowBookForm(data=form_data, initial={'bookcopy_id': book_copy_id})

        self.assertFalse(form.is_valid())
        self.assertIn('due_date', form.errors)
        self.assertEqual(form.errors['due_date'][0], 'Invalid due date - due date cannot be in the past')

  
#####################################################################
class DeclineBorrowingFormTest(TestCase):
    def test_form_initial_data(self):
        initial = {'bookcopy_id': 1, 'borrower_id': 2}
        form = DeclineBorrowingForm(initial=initial)
        self.assertEqual(form.initial['book_copy'], 1)
        self.assertEqual(form.initial['borrower'], 2)
        self.assertTrue(form.fields['book_copy'].disabled)
        self.assertTrue(form.fields['borrower'].disabled)
        self.assertTrue(form.fields['start_date'].disabled)
        self.assertTrue(form.fields['due_date'].disabled)
        self.assertTrue(form.fields['decline_reason'].required)

    def test_invalid_form_submission(self):
        book_copy_id = 1
        borrower_id = 2
        form_data = {
            'book_copy': book_copy_id,
            'borrower': borrower_id,
            'start_date': '2022-12-31',  # Invalid start date in the past
            'due_date': '2022-12-25',  # Invalid due date earlier than start date
            'decline_reason': ''
        }
        form = DeclineBorrowingForm(data=form_data, initial={'bookcopy_id': book_copy_id, 'borrower_id': borrower_id})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 5)
        self.assertIn('start_date', form.errors)
        self.assertIn('due_date', form.errors)
        self.assertIn('decline_reason', form.errors)

    def test_decline_reason_max_length(self):
        book_copy_id = 1
        borrower_id = 2
        max_length = 100
        form_data = {
            'book_copy': book_copy_id,
            'borrower': borrower_id,
            'start_date': '2023-01-01',
            'due_date': '2023-01-15',
            'decline_reason': 'T' * (max_length + 1)  # exceed the max length
        }
        form = DeclineBorrowingForm(data=form_data, initial={'bookcopy_id': book_copy_id, 'borrower_id': borrower_id})
        self.assertFalse(form.is_valid())    
