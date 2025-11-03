from django.urls import path
from .views import RestaurantCreateAPIView, RestaurantListAPIView, RestaurantOrderAction ,CreateItemAPIView ,ListItemsAPIView

urlpatterns = [
    path('', RestaurantListAPIView.as_view(), name='restaurants-list'),
    path('create/', RestaurantCreateAPIView.as_view(), name='restaurant-create'),
    path('order-action/', RestaurantOrderAction.as_view(), name='restaurant-order-action'),
    path('items/create/', CreateItemAPIView.as_view(), name='create-item'),
 
    path('items/<int:restaurant_id>/', ListItemsAPIView.as_view(), name='list-items-by-restaurant'),
]
