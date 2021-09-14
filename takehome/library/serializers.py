from django.contrib.auth.models import User, Permission

from rest_framework import serializers

from .models import *


class AuthorBookSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Book
        fields = ('id', 'title')
        

class AuthorSerializer(serializers.ModelSerializer):
    
    books = AuthorBookSerializer(many=True)
    
    class Meta:
        model = Author
        fields = ('id', 'first_name', 'last_name', 'books')


class AuthorDeserializer(serializers.ModelSerializer):
    
    class Meta:
        model = Author
        fields = ('id', 'first_name', 'last_name', 'books')
        read_only_fields = ('id',)


class BookSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Book
        fields = ('id', 'title', 'publish_year', 'genre', 'authors')
        depth = 1
        

class BookDeserializer(serializers.ModelSerializer):
    
    class Meta:
        model = Book
        fields = ('id', 'title', 'publish_year', 'genre', 'authors')
        read_only_fields = ('id',)
        

class CheckoutsSerializer(serializers.Serializer):
    book_id = serializers.IntegerField()
    book_title = serializers.CharField(max_length=128)
    due_date = serializers.DateField()
    user = serializers.DictField()
    
    class Meta:
        read_only_fields = ('book_id', 'book_title', 'user')
        
    def update(self, instance, validated_data):
        due_date = validated_data.pop('due_date', None)
        instance.due_date = due_date
        instance.save()
        return instance
    

class GenreSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Genre
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    
    role = serializers.SerializerMethodField()
    books = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'role', 'books')
        depth = 2
    
    def get_role(self, obj: User):
        return obj.groups.first().name if obj.groups.exists() else None
    
    def get_books(self, obj: User):
        books = obj.checkout_leger.filter(
            return_time__isnull=True).values_list('book_id', 'book__title')
        return [{'id': book_id, 'title': title} for book_id, title in books]
