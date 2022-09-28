"""
Views for recipe apis
"""

from rest_framework import (
    viewsets,
    mixins,
    status,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from core.models import (
    Recipe,
    Tag,
    Ingredient,
)
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
        if self.action == 'list':
            return self.queryset.filter(
                created_by=self.request.user).order_by('-id')
        return self.queryset.filter(
                created_by=self.request.user).order_by(
                    '-id').prefetch_related('tags', 'ingredients')

    def get_serializer_class(self):
        """
        Return serializer class for request
        """
        if self.action == 'list':
            return serializers.RecipeSerializer

        elif self.action == 'upload_image':
            return serializers.RecipeImageSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """
        Create recipe
        """
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        """
        Update recipe
        """
        serializer.save(updated_by=self.request.user)

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, uuid=None):
        """
        Upload image to recipe
        """
        recipe = self.get_object()
        serializer = self.get_serializer(recipe, data=self.request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TagViewSet(mixins.DestroyModelMixin,
                 mixins.UpdateModelMixin,
                 mixins.ListModelMixin,
                 viewsets.GenericViewSet):
    """
    Manage tags in database
    """

    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()
    permission_classes = [IsAuthenticated]
    lookup_field = "uuid"

    def get_queryset(self):
        """
        Retrieve tags of the user
        """
        return self.queryset.filter(
            created_by=self.request.user).order_by('-name')

    def perform_update(self, serializer):
        """
        Update recipe
        """
        serializer.save(updated_by=self.request.user)


class IngredientViewSet(mixins.DestroyModelMixin,
                        mixins.UpdateModelMixin,
                        mixins.ListModelMixin,
                        viewsets.GenericViewSet):
    """
    Manage ingredients in database
    """
    serializer_class = serializers.IngredientSerializer
    queryset = Ingredient.objects.all()
    permission_classes = [IsAuthenticated]
    lookup_field = "uuid"

    def get_queryset(self):
        """
        Retrieve tags of the user
        """
        return self.queryset.filter(
            created_by=self.request.user).order_by('-name')

    def perform_update(self, serializer):
        """
        Update recipe
        """
        serializer.save(updated_by=self.request.user)
