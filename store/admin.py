from django.contrib import admin
from .models import Category, Book, Review, Order, OrderItem, Profile

admin.site.register([Category, Book, Review, Order, OrderItem, Profile])
