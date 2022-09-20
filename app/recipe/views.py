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
    serializer_class = serializers.RecipeSerializer
    queryset = Recipe.objects.all()
    permission_classes = [IsAuthenticated]
    lookup_field = "uuid"

    def get_queryset(self):
        """
        Retrieve recipe of the user
        """
        return self.queryset.filter(
            created_by=self.request.user).order_by('-id')
