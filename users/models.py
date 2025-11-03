from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # user types
    CUSTOMER = 'CUSTOMER'
    RESTAURANT = 'RESTAURANT'
    DELIVERY = 'DELIVERY'

    USER_TYPE_CHOICES = [
        (CUSTOMER, 'Customer'),
        (RESTAURANT, 'Restaurant'),
        (DELIVERY, 'Delivery Partner'),
    ]

    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default=CUSTOMER)
    # add phone, address fields if needed
    phone_number = models.CharField(max_length=20, blank=True, null=True)
