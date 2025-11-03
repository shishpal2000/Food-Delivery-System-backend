from rest_framework import serializers
from .models import Restaurant , Item
from orders.models import Order
from users.models import User

class RestaurantSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    class Meta:
        model = Restaurant
        fields = ['id', 'owner', 'name', 'address']

class OrderStatusUpdateSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    action = serializers.ChoiceField(choices=['accept', 'prepare'])
 
class ItemSerializer(serializers.ModelSerializer):
    restaurant = RestaurantSerializer(read_only=True)  # For GET (nested)
    restaurant_id = serializers.PrimaryKeyRelatedField(
        queryset=Restaurant.objects.all(), source='restaurant', write_only=True
    )  # For POST

    class Meta:
        model = Item
        fields = ['id', 'restaurant', 'restaurant_id', 'name', 'description', 'price', 'is_available', 'created_at']
        read_only_fields = ['id', 'created_at']