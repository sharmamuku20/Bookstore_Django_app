from django.shortcuts import render
from rest_framework import viewsets, generics, permissions, filters, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from .models import Book, Category, Review, Order
from .serializers import (
    BookSerializer, CategorySerializer, ReviewSerializer,
    OrderSerializer, ProfileSerializer
)
from .permissions import (
    IsAdminOrReadOnly, IsReviewerAndPurchasedBook, IsOwnerOrReadOnly
)

# Public: List all books with pagination, search, filter by category/price
class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all().prefetch_related('reviews').order_by('id')
    serializer_class = BookSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['title', 'author', 'ISBN']
    filterset_fields = ['category', 'price']
    ordering_fields = ['price', 'published_date']

    # Public: Retrieve single book with details and reviews
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        reviews = Review.objects.filter(book=instance)
        review_serializer = ReviewSerializer(reviews, many=True)
        data = serializer.data
        data['reviews'] = review_serializer.data
        return Response(data)

    # Admin: CRUD for books (handled by ModelViewSet + permissions)

# Public: List all categories
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]

    # Admin: CRUD for categories (handled by ModelViewSet + permissions)

# Public: List reviews for a book
class BookReviewListView(generics.ListAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        book_id = self.kwargs['book_id']
        return Review.objects.filter(book_id=book_id)

# Authenticated: Create/update/delete reviews (only if purchased the book)
class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsOwnerOrReadOnly()]
        elif self.action == 'create':
            return [permissions.IsAuthenticated(), IsReviewerAndPurchasedBook()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# Authenticated: Place an order, list user’s past orders
class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer

    def get_queryset(self):
        # Short-circuit for schema generation
        if getattr(self, 'swagger_fake_view', False):
            return Order.objects.none()
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
        if user.is_authenticated:
            return Order.objects.filter(user=user)
        return Order.objects.none()

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        elif self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        elif self.action == 'create':
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    # Admin: Update order status
    @action(detail=True, methods=['patch'], permission_classes=[permissions.IsAdminUser])
    def update_status(self, request, pk=None):
        order = self.get_object()
        status_value = request.data.get('status')
        if status_value not in dict(Order.STATUS_CHOICES):
            return Response({'detail': 'Invalid status.'}, status=status.HTTP_400_BAD_REQUEST)
        order.status = status_value
        order.save(update_fields=['status'])
        return Response({'status': order.status})

# Public: User registration using ProfileSerializer
class UserRegistrationView(generics.CreateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.AllowAny]

# Routers should be set up in urls.py to wire these viewsets.

# All views use DRF's generics and viewsets, with appropriate permissions and serializers.
# No changes needed.
