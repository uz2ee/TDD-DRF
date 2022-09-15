"""
Views for the user api
"""
from rest_framework import generics
from user.serializers import UserSerializer


class CreateUserAPIView(generics.CreateAPIView):
    """
    Create new user
    """
    serializer_class = UserSerializer
