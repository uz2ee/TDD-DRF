"""
Serializer for recipe api
"""

from rest_framework import serializers

from core.models import (
    Recipe,
    Tag
)


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


class RecipeSerializer(serializers.ModelSerializer):
    """
    Serializer for recipe
    """
    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = [
            'uuid',
            'title',
            'time_minutes',
            'price',
            'link',
            'tags'
        ]

    def _get_or_create_tags(self, tags, instance):
        user = self.context['request'].user
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                created_by=user,
                **tag
            )
            instance.tags.add(tag_obj)

    def create(self, validated_data):
        """
        Create recipe
        """
        tags = validated_data.pop('tags', [])
        recipe = Recipe.objects.create(**validated_data)
        self._get_or_create_tags(tags, recipe)
        return recipe

    def update(self, instance, validated_data):
        """
        Update Recipe
        """
        tags = validated_data.pop('tags', None)
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class RecipeDetailSerializer(RecipeSerializer):
    """
    Detailed Serializer for recipe
    """

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']
