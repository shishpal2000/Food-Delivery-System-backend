from django.urls import path
from .views import DeliveryActionAPIView

urlpatterns = [
    path('action/', DeliveryActionAPIView.as_view(), name='delivery-action'),
]
