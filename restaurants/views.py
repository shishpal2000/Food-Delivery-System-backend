from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Restaurant , Item 
from .serializers import RestaurantSerializer, OrderStatusUpdateSerializer , ItemSerializer
from orders.models import Order
from django.shortcuts import get_object_or_404
from orders.events import order_created, order_cancelled
from orders.events import publish_event
from rest_framework.exceptions import PermissionDenied

class RestaurantCreateAPIView(generics.CreateAPIView):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    permission_classes = [permissions.AllowAny]

    # def perform_create(self, serializer):
    #     # only restaurant user can create restaurant
    #     if self.request.user.user_type != self.request.user.RESTAURANT:
    #         raise PermissionError("Only users of type RESTAURANT can create restaurant entries")
    #     serializer.save(owner=self.request.user)

class RestaurantListAPIView(generics.ListAPIView):
    queryset=Restaurant.objects.all()
    
    serializer_class = RestaurantSerializer
    permission_classes = [permissions.IsAuthenticated]

    # def get_queryset(self):
    #     user = self.request.user

    #     # Allow only restaurant owners
    #     if user.user_type != user.RESTAURANT_OWNER:
    #         raise PermissionDenied("Only restaurant owners can view their restaurants.")

# Endpoints for restaurant to accept/prepare orders
from rest_framework.views import APIView

class RestaurantOrderAction(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # request.data: { "order_id": 1, "action": "accept" }
        serializer = OrderStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order_id = serializer.validated_data['order_id']
        action = serializer.validated_data['action']
        order = get_object_or_404(Order, id=order_id)

        # check that the logged in user is owner of the restaurant for that order
        if request.user.user_type != request.user.RESTAURANT:
            return Response({'detail': 'Only restaurant users can perform this action'}, status=status.HTTP_403_FORBIDDEN)

        # For simplicity require the restaurant that owns the order.restaurant matches user's owned restaurant
        # If there's a one-to-one mapping: check owner - skipping complicated multi-restaurant logic here
        print("jai maa kali", request.user)
        print("jai maa shiv", order.restaurant.owner)
        if order.restaurant.owner != request.user:
            return Response({'detail':'Not your restaurant order'}, status=status.HTTP_403_FORBIDDEN)
        

        if action == 'accept':
            if order.status != Order.PENDING:
                return Response({'detail':'Order not in PENDING state'}, status=status.HTTP_400_BAD_REQUEST)
            order.status = Order.ACCEPTED
            order.save()
            # publish event for delivery service maybe to know it's accepted
            publish_event('order.accepted', {'order_id': order.id})
            return Response({'detail':'Order accepted', 'order_id': order.id})
        elif action == 'prepare':
            if order.status != Order.ACCEPTED:
                return Response({'detail':'Order must be ACCEPTED to prepare'}, status=status.HTTP_400_BAD_REQUEST)
            order.status = Order.PREPARED
            order.save()
            publish_event('order.prepared', {'order_id': order.id})
            return Response({'detail':'Order marked PREPARED', 'order_id': order.id})
        else:
            return Response({'detail':'Unknown action'}, status=status.HTTP_400_BAD_REQUEST)


class CreateItemAPIView(generics.CreateAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [permissions.AllowAny]



class ListItemsAPIView(generics.ListAPIView):
    serializer_class = ItemSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        restaurant_id = self.kwargs.get('restaurant_id')
        return Item.objects.filter(restaurant_id=restaurant_id).select_related('restaurant')