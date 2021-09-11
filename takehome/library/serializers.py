from django.contrib.auth.models import User, Permission

from rest_framework import serializers

from .models import *


class AuthorListSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Author
        fields = ('id', 'first_name', 'last_name')

    
class AuthorSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Author
        fields = ('id', 'first_name', 'last_name', 'books')
        list_serializer_class = AuthorListSerializer
        depth = 1


class BookSerializer(serializers.ModelSerializer):
    
    available_for_checkout = serializers.SerializerMethodField()
    
    class Meta:
        model = Book
        fields = ('id', 'title', 'publish_year', 'genre', 'authors', 'available_for_checkout')
        depth = 1
        
    def get_available_for_checkout(self, obj):
        #return obj.books
        return None


class BookDeserializer(serializers.ModelSerializer):
    
    class Meta:
        model = Book
        fields = ('id', 'title', 'publish_year', 'genre', 'authors')
        read_only_fields = ('id',)
    

class GenreSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Genre
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    
    role = serializers.SerializerMethodField()
    books = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'role', 'books')
    
    def get_role(self, obj):
        return obj.groups.first().name if obj.groups.exists() else None
    
    def get_books(self, obj):
        return "asdf"