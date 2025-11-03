from django.urls import path
from .views import PlaceOrderAPIView, OrderDetailAPIView, CancelOrderAPIView,PendingOrderListAPIView,PreparedOrderListAPIView, ListCustomerOrdersAPIView, acceptOrderListAPIView,pickedOrderListAPIView

urlpatterns = [
    path('place/', PlaceOrderAPIView.as_view(), name='place-order'),
    path('<int:pk>/', OrderDetailAPIView.as_view(), name='order-detail'),
    path('<int:pk>/cancel/', CancelOrderAPIView.as_view(), name='order-cancel'),
    path('pending/', PendingOrderListAPIView.as_view(), name='pending-orders'),
    path('prepared/', PreparedOrderListAPIView.as_view(), name='prepared-orders'),
    path('accept/', acceptOrderListAPIView.as_view(), name='accept-orders'),
    path('picked/', pickedOrderListAPIView.as_view(), name='picked-orders'),
    #  path('<int:pk>/', OrderDetailAPIView.as_view(), name='item-list'),
    path('orders/', ListCustomerOrdersAPIView.as_view(), name='orders'),
]
