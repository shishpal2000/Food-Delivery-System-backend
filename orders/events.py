from django.dispatch import Signal

# Define signals
order_created = Signal()
order_cancelled = Signal()

def publish_event(event_name, payload):
    if event_name == 'order.created':
        order_created.send(sender='orders', payload=payload)
    elif event_name == 'order.cancelled':
        order_cancelled.send(sender='orders', payload=payload)
    elif event_name == 'order.accepted':
        order_created.send(sender='orders', payload=payload)
    elif event_name == 'order.prepared':
        order_created.send(sender='orders', payload=payload)
    elif event_name == 'order.picked_up':
        order_created.send(sender='orders', payload=payload)
    elif event_name == 'order.delivered':
        order_created.send(sender='orders', payload=payload)
