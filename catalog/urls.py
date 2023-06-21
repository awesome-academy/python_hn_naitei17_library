from django.urls import path
from . import views
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
openapi.Info(
        title="Simple API",
        default_version='v1',
        description="An simple API for CRUD with Article",
        contact=openapi.Contact(email="contact@education.sun.local"),
        license=openapi.License(name="Sun Education License"),
        ),
        public=True,
        permission_classes=(permissions.AllowAny,),
    )

# guest
urlpatterns = [
    path('', views.index, name='index'),
    path('books/', views.BookListView.as_view(), name='books'),
    path('book/<int:pk>', views.BookDetailView.as_view(), name='book-detail'),
]

urlpatterns += [
    path('api/v1/register/', views.RegisterAPI.as_view(), name='api-register'),
    path('api/v1/login/', views.LoginAPI.as_view(), name='api-login'),
    path('api/v1/search-book/', views.SearchBookAPI.as_view(), name='search-book'),
    path('api/v1/create-borrow-book/', views.BorrowBookAPI.as_view(), name='borrow-book'),
    path('api/v1/pending-borrowing/', views.PendingBorrowingAPI.as_view(), name='pending-borrowing'),
    path('api/v1/pending-borrowing/update-status/<int:id>', views.ProcessBorrowBookAPI.as_view(), name='update-status'),
]

urlpatterns += [
    path('swagger', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
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
    path('borrowing/<int:pk>/request-return/', views.request_return_book, name='borrowing-request-return'),
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
