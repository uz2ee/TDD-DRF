"""
Test for ingredient apis
"""


from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Ingredient

from recipe.serializers import (
    IngredientSerializer,
)

from core.tests.test_models import (
    create_user,
    create_ingredient,
    create_ingredient,
)

INGREDIENTS_URL = reverse('recipe:ingredient-list')


def detail_url(ingredient_uuid):
    """
    Create and return a ingredient details url
    """
    return reverse('recipe:ingredient-detail', args=[ingredient_uuid])


class PublicIngredientAPITests(TestCase):
    """
    Test public ingredient apis
    """

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """
        Test retrieve ingredients
        """
        result = self.client.get(INGREDIENTS_URL)

        self.assertEqual(result.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientAPITests(TestCase):
    """
    Test authenticated ingredient apis
    """

    def setUp(self):
        self.user = create_user(
            email='test@example.com',
            password='test_password',
            name='Test Name'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_ingredient(self):
        """
        Test retrieve ingredient list
        """
        create_ingredient(user=self.user, name="Kale")
        create_ingredient(user=self.user, name="Vanilla")

        result = self.client.get(INGREDIENTS_URL)

        ingredients = ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data, serializer.data)

    def test_retrieve_user_limited_ingredient_list(self):
        """
        Test retrieve ingredient list
        """

        self.other_user = create_user(
            email='test2@example.com',
            password='test2_password',
            name='Test Name 2'
        )
        create_ingredient(self.user)
        create_ingredient(self.user)
        create_ingredient(self.other_user)
        create_ingredient(self.other_user)

        result = self.client.get(ingredientS_URL)

        ingredients = Ingredient.objects.filter(created_by=self.user).order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data, serializer.data)

    def test_patch_ingredient(self):
        """
        Test ingredient update
        """

        ingredient = create_ingredient(
            user=self.user,
            name='Sample name'
        )
        payload = {
            'name': 'New name'
        }
        url = detail_url(ingredient.uuid)
        result = self.client.patch(url, payload)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        ingredient.refresh_from_db()
        self.assertEqual(ingredient.name, payload['name'])
        self.assertEqual(ingredient.created_by, self.user)
        self.assertEqual(ingredient.updated_by, self.user)

    def test_put_ingredient(self):
        """
        Test ingredient update
        """

        ingredient = create_ingredient(
            user=self.user,
            name='Sample name'
        )
        payload = {
            'name': 'New name'
        }
        url = detail_url(ingredient.uuid)
        result = self.client.put(url, payload)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        ingredient.refresh_from_db()
        self.assertEqual(ingredient.name, payload['name'])
        self.assertEqual(ingredient.created_by, self.user)
        self.assertEqual(ingredient.updated_by, self.user)

    def test_put_ingredient_unsecssful(self):
        """
        Test ingredient update fail correctly for missing params
        """
        ingredient = create_ingredient(
            user=self.user,
            name='Sample Name'
        )
        payload = {}

        url = detail_url(ingredient.uuid)
        result = self.client.put(url, payload)

        self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_ingredient_unsecssful(self):
        """
        Test ingredient update user fail correctly
        """
        ingredient = create_ingredient(
            user=self.user,
            name='Sample Name'
        )
        new_user = create_user(
            email='test2@example.com',
            password='test2_password',
            name='Test Name 2'
        )
        payload = {
            'created_by': new_user.id
        }

        url = detail_url(ingredient.uuid)
        result = self.client.put(url, payload)

        self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_ingredient(self):
        """
        Test delete ingredient
        """
        ingredient = create_ingredient(user=self.user)

        url = detail_url(ingredient.uuid)
        result = self.client.delete(url)

        self.assertEqual(result.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(ingredient.objects.filter(uuid=ingredient.uuid).exists())

    def test_delete_ingredient_of_other_user(self):
        """
        Test delete ingredient of other users
        """
        new_user = create_user(
            email='test2@example.com',
            password='test2_password',
            name='Test Name 2'
        )
        ingredient = create_ingredient(user=new_user)

        url = detail_url(ingredient.uuid)
        result = self.client.delete(url)

        self.assertEqual(result.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(ingredient.objects.filter(uuid=ingredient.uuid).exists())
