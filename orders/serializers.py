# orders/serializers.py
from rest_framework import serializers
from .models import Order
from restaurants.models import Restaurant, Item
from restaurants.serializers import RestaurantSerializer, ItemSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]

class OrderSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer(read_only=True)
    restaurant = RestaurantSerializer(read_only=True)
    restaurant_id = serializers.PrimaryKeyRelatedField(
        queryset=Restaurant.objects.all(), source='restaurant', write_only=True
    )
    items = ItemSerializer(many=True, read_only=True)
    item_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Item.objects.all(), source='items', write_only=True
    )

    class Meta:
        model = Order
        fields = [
            'id', 'customer', 'restaurant', 'restaurant_id', 'items', 'item_ids',
             'status', 'created_at'
        ]
        read_only_fields = ['id', 'customer', 'status', 'created_at']

    def create(self, validated_data):
        items = validated_data.pop('items', [])
        order = Order.objects.create(**validated_data)
        order.items.set(items)
        # order.total_price = sum(item.price for item in order.items.all())
        order.save()
        return order