from rest_framework import serializers
from django.contrib.auth.models import User

from .models import Book, Borrowing

# User Serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')

# Register Serializer
class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(validated_data['username'], validated_data['email'], validated_data['password'])

        return user

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ('title', 'summary', 'author', 'genre', 'language')

class ProcessBorrowBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ('borrower', 'book_copy', 'start_date', 'due_date')

class BorrowBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ('borrower', 'book_copy', 'start_date', 'due_date', 'decline_reason', 'status')
