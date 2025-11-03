from rest_framework.views import APIView
from rest_framework import permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from orders.models import Order
from orders.events import publish_event

class DeliveryActionAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        Payload: { "order_id": 1, "action": "pickup" | "deliver" }
        """
        order_id = request.data.get('order_id')
        action = request.data.get('action')
        order = get_object_or_404(Order, id=order_id)

        if request.user.user_type != request.user.DELIVERY:
            return Response({'detail':'Only delivery partners can perform this action'}, status=status.HTTP_403_FORBIDDEN)

        # For real systems, check that the delivery partner is assigned to the order or accept assignment
        # For this prototype, we assign the delivery partner when they pick up
        if action == 'pickup':
            if order.status != Order.PREPARED:
                return Response({'detail':'Order must be PREPARED before pickup'}, status=status.HTTP_400_BAD_REQUEST)
            order.status = Order.PICKED_UP
            order.delivery_partner = request.user
            order.save()
            publish_event('order.picked_up', {'order_id': order.id})
            return Response({'detail':'Order picked up', 'order_id': order.id})

        elif action == 'deliver':
            if order.status != Order.PICKED_UP:
                return Response({'detail':'Order must be PICKED_UP to deliver'}, status=status.HTTP_400_BAD_REQUEST)
            if order.delivery_partner != request.user:
                return Response({'detail':'You are not the assigned delivery partner'}, status=status.HTTP_403_FORBIDDEN)
            order.status = Order.DELIVERED
            order.save()
            publish_event('order.delivered', {'order_id': order.id})
            return Response({'detail':'Order delivered', 'order_id': order.id})
        else:
            return Response({'detail':'Unknown action'}, status=status.HTTP_400_BAD_REQUEST)
