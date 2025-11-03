from django.urls import path
from .views import UserCreateAPIView, LoginAPIView

urlpatterns = [
    path('register/', UserCreateAPIView.as_view(), name='user-register'),
    path('login/', LoginAPIView.as_view(), name='login'),
]
