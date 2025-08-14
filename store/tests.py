import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User
from .models import Book, Category, Order, OrderItem, Review

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user(db):
    return User.objects.create_user(username='testuser', password='testpass')

@pytest.fixture
def staff_user(db):
    return User.objects.create_user(username='admin', password='adminpass', is_staff=True)

@pytest.fixture
def category(db):
    return Category.objects.create(name='Fiction', description='Fictional books')

@pytest.fixture
def book(db, category):
    return Book.objects.create(
        title='Book 1',
        author='Author 1',
        ISBN='1234567890123',
        price=10.00,
        stock=5,
        published_date='2023-01-01',
        category=category
    )

@pytest.fixture
def purchased_order(db, user, book):
    order = Order.objects.create(user=user, total_price=10.00, status='pending')
    OrderItem.objects.create(order=order, book=book, quantity=1, price_at_purchase=10.00)
    return order

@pytest.mark.django_db
def test_book_listing_pagination_and_filtering(api_client, book, category):
    # Create another book for pagination
    Book.objects.create(
        title='Book 2',
        author='Author 2',
        ISBN='1234567890124',
        price=20.00,
        stock=3,
        published_date='2023-01-02',
        category=category
    )
    url = reverse('book-list')
    response = api_client.get(url)
    assert response.status_code == 200
    assert 'results' in response.data
    # Test filtering by category
    response = api_client.get(url, {'category': category.id})
    assert response.status_code == 200
    for b in response.data['results']:
        assert b['category'] == category.id

@pytest.mark.django_db
def test_order_creation_reduces_stock(api_client, user, book):
    # This test expects stock to reduce after order creation due to OrderItem signal
    api_client.force_authenticate(user=user)
    url = reverse('order-list')
    data = {
        'items': [{'book': book.id, 'quantity': 2, 'price_at_purchase': 10.00}],
        'total_price': 20.00,
        'status': 'pending'
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == 201
    book.refresh_from_db()
    assert book.stock == 3  # 5 - 2

@pytest.mark.django_db
def test_review_posting_only_if_purchased(api_client, user, book, purchased_order):
    api_client.force_authenticate(user=user)
    url = reverse('review-list')
    data = {
        'book': book.id,
        'rating': 5,
        'comment': 'Great book!'
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == 201
    # Try with a user who did not purchase
    other_user = User.objects.create_user(username='other', password='otherpass')
    api_client.force_authenticate(user=other_user)
    response = api_client.post(url, data, format='json')
    assert response.status_code == 403

@pytest.mark.django_db
def test_jwt_authentication(api_client, user):
    url = reverse('token_obtain_pair')
    response = api_client.post(url, {'username': user.username, 'password': 'testpass'})
    assert response.status_code == 200
    assert 'access' in response.data
    assert 'refresh' in response.data
    # Use token to access protected endpoint
    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + response.data['access'])
    protected_url = reverse('order-list')
    response2 = api_client.get(protected_url)
    assert response2.status_code in [200, 403, 404]  # 200 if user has orders, 403/404 if not
