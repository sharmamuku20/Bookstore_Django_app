from rest_framework import permissions
from .models import Order, Book

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Allow GET, HEAD, OPTIONS for everyone; write actions only for staff.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff

class IsReviewerAndPurchasedBook(permissions.BasePermission):
    """
    Allow review creation only if user has purchased the book in an order.
    """
    def has_permission(self, request, view):
        if request.method != 'POST':
            return True
        user = request.user
        book_id = request.data.get('book')
        if not user or not user.is_authenticated or not book_id:
            return False
        # Check if user has an order with this book
        return Order.objects.filter(user=user, items__book_id=book_id).exists()

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Allow editing/deleting only if the object belongs to the requesting user.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        # Assumes the object has a 'user' attribute
        return hasattr(obj, 'user') and obj.user == request.user
