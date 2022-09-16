"""
Views for the user api
"""
from rest_framework import generics
from user.serializers import UserSerializer
from rest_framework import permissions


class CreateUserAPIView(generics.CreateAPIView):
    """
    Create new user
    """
    serializer_class = UserSerializer


class RetrieveUpdateUserAPIView(generics.RetrieveUpdateAPIView):
    """
    Update old user
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """
        Retrieve and return authenticated user
        """
        return self.request.user
