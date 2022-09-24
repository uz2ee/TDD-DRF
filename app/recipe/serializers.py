"""
Serializer for recipe api
"""

from rest_framework import serializers

from core.models import (
    Recipe,
    Tag
)


class RecipeSerializer(serializers.ModelSerializer):
    """
    Serializer for recipe
    """

    class Meta:
        model = Recipe
        fields = [
            'uuid',
            'title',
            'time_minutes',
            'price',
            'link'
        ]


class RecipeDetailSerializer(RecipeSerializer):
    """
    Detailed Serializer for recipe
    """

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']


class TagSerializer(serializers.ModelSerializer):
    """
    Serialzier for tags
    """
    class Meta:
        model = Tag
        fields = [
            'uuid',
            'name',
        ]
