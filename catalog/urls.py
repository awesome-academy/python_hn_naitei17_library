from django.urls import path
from django.conf import settings
from . import views

# guest
urlpatterns = [
    path('', views.index, name='index'),
    path('books/', views.BookListView.as_view(), name='books'),
    path('book/<int:pk>', views.BookDetailView.as_view(), name='book-detail'),
]

urlpatterns += [
    path('authors/', views.AuthorListView.as_view(), name='authors'),
    path('author/<int:pk>', views.AuthorDetailView.as_view(), name='author-detail'),
]

# user
urlpatterns += [
    path('borrowing/', views.BorrowingByUserListView.as_view(), name='borrowing-list'),
]

urlpatterns += [
    path('book/<int:book_id>/review/create/', views.review_book, name='review-create'),
    path('book/<int:book_id>/borrowing/create/<uuid:bookcopy_id>', views.borrow_book, name='borrowing-create'),
]

urlpatterns += [
    # path('borrowing/create/<uuid:bookcopy_id>', views.borrow_book, name='borrowing-create'),
    path('borrowing/<int:pk>/cancel/', views.cancel_borrowing, name='borrowing-cancel'),
]

# librarian
urlpatterns += [
    path('allborrowing/', views.BorrowingByStaffListView.as_view(), name='all-borrowing'),
]

urlpatterns += [
    path('borrowing/<int:pk>/approve/', views.approve_borrowing, name='borrowing-approve'),
    path('borrowing/<int:pk>/decline/', views.decline_borrowing, name='borrowing-decline'),
    path('borrowing/<int:pk>/start/', views.start_borrowing, name='borrowing-start'),
    path('borrowing/<int:pk>/end/', views.end_borrowing, name='borrowing-end'),
]

urlpatterns += [
    path('author/create/', views.AuthorCreate.as_view(), name='author-create'),
    path('author/<int:pk>/update/', views.AuthorUpdate.as_view(), name='author-update'),
    path('author/<int:pk>/delete/', views.AuthorDelete.as_view(), name='author-delete'),
]

urlpatterns += [
    path('book/create/', views.BookCreate.as_view(), name='book-create'),
    path('book/<int:pk>/update/', views.BookUpdate.as_view(), name='book-update'),
    path('book/<int:pk>/delete/', views.BookDelete.as_view(), name='book-delete'),
]
