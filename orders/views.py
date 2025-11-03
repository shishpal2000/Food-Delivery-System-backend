from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Order
from .serializers import OrderSerializer
from django.shortcuts import get_object_or_404
from .events import publish_event
from rest_framework.exceptions import PermissionDenied

class PlaceOrderAPIView(generics.CreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        print("66666666666666666", user)

        # ensure only customer can place orders
        if user.user_type != user.CUSTOMER:
            raise PermissionDenied("Only customers can place orders.")

        # validate and save order
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save(customer=user)

        # notify restaurant via signal/event
        publish_event('order.created', {'order_id': order.id})

        # return response
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class OrderDetailAPIView(generics.RetrieveAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

class CancelOrderAPIView(generics.GenericAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        # only owner customer can cancel
        if order.customer != request.user:
            return Response({'detail': 'Not allowed'}, status=status.HTTP_403_FORBIDDEN)
        if not order.can_cancel():
            return Response({'detail': 'Only PENDING orders can be cancelled'}, status=status.HTTP_400_BAD_REQUEST)
        order.cancel()
        publish_event('order.cancelled', {'order_id': order.id})
        return Response(self.get_serializer(order).data)
    

class PendingOrderListAPIView(generics.ListAPIView):
    queryset = Order.objects.filter(status='PENDING')
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]


# 2️⃣ Prepared Orders API
class PreparedOrderListAPIView(generics.ListAPIView):
    queryset = Order.objects.filter(status='PREPARED')
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

class acceptOrderListAPIView(generics.ListAPIView):
    queryset = Order.objects.filter(status='ACCEPTED')
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

class pickedOrderListAPIView(generics.ListAPIView):
    queryset = Order.objects.filter(status='PICKED_UP')
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]


class ListCustomerOrdersAPIView(generics.ListAPIView):
    """
    List all orders placed by the logged-in customer only.
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        # ✅ Only allow customers
        if user.user_type != user.CUSTOMER:
            raise PermissionDenied("Only customers can view their own orders.")

        # ✅ Return only orders placed by this logged-in customer
        return Order.objects.filter(customer=user).order_by('-created_at')
    