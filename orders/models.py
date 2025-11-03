from django.db import models
from restaurants.models import Item
from django.conf import settings
from django.utils import timezone

class Order(models.Model):
    PENDING = 'PENDING'
    ACCEPTED = 'ACCEPTED'
    PREPARED = 'PREPARED'
    PICKED_UP = 'PICKED_UP'
    DELIVERED = 'DELIVERED'
    CANCELLED = 'CANCELLED'

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (ACCEPTED, 'Accepted'),
        (PREPARED, 'Prepared'),
        (PICKED_UP, 'Picked Up'),
        (DELIVERED, 'Delivered'),
        (CANCELLED, 'Cancelled'),
    ]

    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    restaurant = models.ForeignKey('restaurants.Restaurant', on_delete=models.CASCADE, related_name='orders')
    delivery_partner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='deliveries')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    # order details: simplified as JSON/text
  
    items = models.ManyToManyField(Item, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def can_cancel(self):
        return self.status == self.PENDING

    def cancel(self):
        if not self.can_cancel():
            raise ValueError("Cannot cancel non-pending order")
        self.status = self.CANCELLED
        self.save()
