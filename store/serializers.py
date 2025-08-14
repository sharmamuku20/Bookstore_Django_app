from rest_framework import serializers
from django.db.models import Avg
from django.contrib.auth.models import User
from .models import Category, Book, Review, Order, OrderItem, Profile

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class BookSerializer(serializers.ModelSerializer):
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = '__all__'

    def get_average_rating(self, obj):
        avg = obj.reviews.aggregate(avg=Avg('rating'))['avg']
        return round(avg, 2) if avg is not None else None

class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Review
        fields = '__all__'

    def validate(self, data):
        request = self.context.get('request')
        user = request.user if request else None
        book = data.get('book')
        if self.instance is None and user and book:
            # Only on create, not update
            if Review.objects.filter(user=user, book=book).exists():
                raise serializers.ValidationError("You have already reviewed this book. Please update your review instead.")
        return data

    def validate_rating(self, value):
        if not (1 <= value <= 5):
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value

class OrderItemBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'ISBN', 'price']

class OrderItemSerializer(serializers.ModelSerializer):
    book = OrderItemBookSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'book', 'quantity', 'price_at_purchase']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'items', 'total_price', 'status', 'order_date']
        read_only_fields = ['id', 'user', 'items', 'total_price', 'status', 'order_date']

    def validate(self, data):
        # Only validate on creation
        if self.instance is not None:
            return data
        request = self.context.get('request')
        items_data = request.data.get('items') if request else None
        if not items_data:
            raise serializers.ValidationError("Order must have at least one item.")
        for item in items_data:
            try:
                book = Book.objects.get(pk=item['book'])
            except Book.DoesNotExist:
                raise serializers.ValidationError(f"Book with id {item['book']} does not exist.")
            if book.stock < int(item['quantity']):
                raise serializers.ValidationError(
                    f"Not enough stock for '{book.title}'. Available: {book.stock}, requested: {item['quantity']}"
                )
        return data
    
    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        items_data = request.data.get('items')
        total_price = 0
        order = Order.objects.create(user=user, total_price=0)  # temp price

        for item in items_data:
            book = Book.objects.get(pk=item['book'])
            quantity = int(item['quantity'])
            price = book.price * quantity
            total_price += price
            OrderItem.objects.create(
                order=order,
                book=book,
                quantity=quantity,
                price_at_purchase=book.price
            )
        order.total_price = total_price
        order.save(update_fields=['total_price'])
        return order

class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = Profile
        fields = ['username', 'password', 'email', 'address', 'phone']

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with that username already exists.")
        return value

    def validate_phone(self, value):
        if Profile.objects.filter(phone=value).exists():
            raise serializers.ValidationError("A profile with that phone number already exists.")
        return value

    def validate_address(self, value):
        if Profile.objects.filter(address=value).exists():
            raise serializers.ValidationError("A profile with that address already exists.")
        return value

    def create(self, validated_data):
        username = validated_data.pop('username')
        password = validated_data.pop('password')
        email = validated_data.pop('email', '')
        user = User.objects.create_user(username=username, email=email, password=password)
        profile = Profile.objects.create(user=user, **validated_data)
        return profile
