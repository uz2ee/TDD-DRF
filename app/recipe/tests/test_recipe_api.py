"""
Test for recipe apis
"""

from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Recipe

from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer,
)

RECIPES_URL = reverse('recipe:recipe-list')


def detail_url(recipe_uuid):
    """
    Create and return a recipe details url
    """
    return reverse('recipe:recipe-detail', args=[recipe_uuid])


def create_recipe(user, **params):
    """
    Create and returns a new recipe
    """
    defaults = {
        'title': 'Sample recipe title',
        'time_minutes': 10,
        'price': Decimal('5.75'),
        'description': 'Sample description',
        'link': 'http://example.com/recipe.pdf'
    }
    defaults.update(params)
    return Recipe.objects.create(created_by=user, **defaults)


class PublicRecipeAPITests(TestCase):
    """
    Test public recipe apis
    """

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """
        Test retrieve recipe
        """
        result = self.client.get(RECIPES_URL)

        self.assertEqual(result.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITests(TestCase):
    """
    Test authenticated recipe apis
    """

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='test@example.com',
            password='test_password',
            name='Test Name'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_recipe(self):
        """
        Test retrieve recipe list
        """
        create_recipe(self.user)
        create_recipe(self.user)

        result = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data, serializer.data)

    def test_retrieve_user_limited_recipe_list(self):
        """
        Test retrieve recipe list
        """

        self.other_user = get_user_model().objects.create_user(
            email='test2@example.com',
            password='test2_password',
            name='Test Name 2'
        )
        create_recipe(self.user)
        create_recipe(self.user)
        create_recipe(self.other_user)
        create_recipe(self.other_user)

        result = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(created_by=self.user).order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data, serializer.data)

    def test_get_recipe_detail(self):
        """
        Test recipe details
        """
        recipe = create_recipe(user=self.user)

        url = detail_url(recipe.uuid)
        result = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(result.data, serializer.data)
