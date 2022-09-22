"""
Views for recipe apis
"""

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from core.models import Recipe
from recipe import serializers


class RecipeViewSet(viewsets.ModelViewSet):
    """
    View to manage recipe apis
    """
    serializer_class = serializers.RecipeDetailSerializer
    queryset = Recipe.objects.all()
    permission_classes = [IsAuthenticated]
    lookup_field = "uuid"

    def get_queryset(self):
        """
        Retrieve recipe of the user
        """
        return self.queryset.filter(
            created_by=self.request.user).order_by('-id')

    def get_serializer_class(self):
        """
        Return serializer class for request
        """
        if self.action == 'list':
            return serializers.RecipeSerializer
        return self.serializer_class
