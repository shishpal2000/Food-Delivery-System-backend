# restaurants/signals.py
from django.dispatch import receiver
from orders.events import order_created, order_cancelled
from .models import Restaurant
from orders.models import Order

@receiver(order_created)
def handle_order_created(sender, payload, **kwargs):
    order_id = payload.get('order_id')
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return
    # Here restaurant app learns about new order. In real microservice you'd send an HTTP request
    # or push to a message queue. For prototype, we can log or store a flag.
    # Example: we print or create a Notification model (omitted). For now: simple print:
    print(f"[restaurants] New order created: order_id={order.id} for restaurant={order.restaurant.name}")

@receiver(order_cancelled)
def handle_order_cancelled(sender, payload, **kwargs):
    order_id = payload.get('order_id')
    print(f"[restaurants] Order cancelled event for id={order_id}")
