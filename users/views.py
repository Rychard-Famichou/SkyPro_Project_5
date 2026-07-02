from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView

from users.serializers import CustomTokenObtainPairSerializer, CustomUserSerializer


# Create your views here.
class CustomTokenObtainPairView(TokenObtainPairView):
    """Create a new token for our user"""
    serializer_class = CustomTokenObtainPairSerializer


class CustomUserCreateView(generics.CreateAPIView):
    """Create a new user in the system"""
    serializer_class = CustomUserSerializer
    permission_classes = [AllowAny]
