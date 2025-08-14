from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Avg
from .models import Order, OrderItem, Review, Book

@receiver(post_save, sender=OrderItem)
def reduce_stock_on_order_item(sender, instance, created, **kwargs):
    if created:
        book = instance.book
        book.stock = max(0, book.stock - instance.quantity)
        book.save(update_fields=['stock'])

