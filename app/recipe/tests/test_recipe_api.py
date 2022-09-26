"""
Test for recipe apis
"""

from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import (
    Recipe,
    Tag,
    Ingredient,
)

from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer,
)

from core.tests.test_models import (
    create_user,
    create_recipe,
    create_tag,
    create_ingredient,
)

RECIPES_URL = reverse('recipe:recipe-list')


def detail_url(recipe_uuid):
    """
    Create and return a recipe details url
    """
    return reverse('recipe:recipe-detail', args=[recipe_uuid])


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
        self.user = create_user(
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

        self.other_user = create_user(
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

    def test_create_recipe(self):
        """
        Test create recipe api
        """

        payload = {
            'title': 'Sample recipe title',
            'time_minutes': 15,
            'price': Decimal('2.75'),
            'description': 'Sample description',
            'link': 'http://example.com/recipe.pdf'
        }

        result = self.client.post(RECIPES_URL, payload)

        self.assertEqual(result.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(uuid=result.data['uuid'])
        self.assertEqual(recipe.created_by, self.user)
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)

    def test_patch_recipe(self):
        """
        Test recipe update
        """

        original_url = 'https://example.com/'
        recipe = create_recipe(
            user=self.user,
            title='Sample title',
            link=original_url
        )
        payload = {
            'title': 'New title'
        }
        url = detail_url(recipe.uuid)
        result = self.client.patch(url, payload)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.link, original_url)
        self.assertEqual(recipe.created_by, self.user)
        self.assertEqual(recipe.updated_by, self.user)

    def test_put_recipe(self):
        """
        Test recipe update
        """
        recipe = create_recipe(
            user=self.user,
            title='Sample title',
            link='https://example.com/',
            description='description old'
        )
        payload = {
            'title': 'New title',
            'link': 'https://example.com/new',
            'description': 'new',
            'time_minutes': 10,
            'price': Decimal('3.00')
        }

        url = detail_url(recipe.uuid)
        result = self.client.put(url, payload)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.created_by, self.user)
        self.assertEqual(recipe.updated_by, self.user)

    def test_put_recipe_unsecssful(self):
        """
        Test recipe update fail correctly for missing params
        """
        recipe = create_recipe(
            user=self.user,
            title='Sample title',
            link='https://example.com/',
            description='description old'
        )
        payload = {
            'title': 'New title',
            'link': 'https://example.com/new',
            'description': 'new',
            'time_minutes': 10,
        }

        url = detail_url(recipe.uuid)
        result = self.client.put(url, payload)

        self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_recipe_unsecssful(self):
        """
        Test recipe update user fail correctly
        """
        recipe = create_recipe(
            user=self.user,
            title='Sample title',
            link='https://example.com/',
            description='description old'
        )
        new_user = create_user(
            email='test2@example.com',
            password='test2_password',
            name='Test Name 2'
        )
        payload = {
            'created_by': new_user.id
        }

        url = detail_url(recipe.uuid)
        result = self.client.put(url, payload)

        self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_recipe_user_validation(self):
        """
        Test recipe update user fail correctly
        """
        recipe = create_recipe(
            user=self.user,
            title='Sample title',
            link='https://example.com/',
            description='description old'
        )
        new_user = create_user(
            email='test2@example.com',
            password='test2_password',
            name='Test Name 2'
        )
        payload = {
            'created_by': new_user.id
        }

        url = detail_url(recipe.uuid)
        result = self.client.put(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.created_by, self.user)
        self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_recipe(self):
        """
        Test delete recipe
        """
        recipe = create_recipe(user=self.user)

        url = detail_url(recipe.uuid)
        result = self.client.delete(url)

        self.assertEqual(result.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(uuid=recipe.uuid).exists())

    def test_delete_recipe_of_other_user(self):
        """
        Test delete recipe of other users
        """
        new_user = create_user(
            email='test2@example.com',
            password='test2_password',
            name='Test Name 2'
        )
        recipe = create_recipe(user=new_user)

        url = detail_url(recipe.uuid)
        result = self.client.delete(url)

        self.assertEqual(result.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(uuid=recipe.uuid).exists())

    def test_cerate_recipe_with_tag(self):
        """
        Test creating recipe with tags
        """
        payload = {
            'title': 'New title',
            'link': 'https://example.com/new',
            'description': 'new',
            'time_minutes': 10,
            'price': Decimal('3.00'),
            'tags': [
                {'name': 'Thai'},
                {'name': 'Dinner'},
                {'name': 'Spicy'}
            ]
        }

        result = self.client.post(RECIPES_URL, payload, format='json')

        self.assertEqual(result.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.filter(created_by=self.user).first()
        self.assertEqual(recipe.created_by, self.user)
        self.assertEqual(recipe.tags.count(), 3)
        for tag in payload['tags']:
            exists = recipe.tags.filter(
                name=tag['name'],
                created_by=self.user
                ).exists()
            self.assertTrue(exists)

    def test_create_recipe_with_exisiting_tag(self):
        """
        Test recipe with exisiting tags
        """

        tag = create_tag(user=self.user, name='Indian')

        payload = {
            'title': 'New title',
            'link': 'https://example.com/new',
            'description': 'new',
            'time_minutes': 10,
            'price': Decimal('3.00'),
            'tags': [
                {'name': 'Indian'},
                {'name': 'Breakfast'},
                {'name': 'Spicy'}
            ]
        }

        result = self.client.post(RECIPES_URL, payload, format='json')

        self.assertEqual(result.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.filter(created_by=self.user).first()
        self.assertEqual(recipe.created_by, self.user)
        self.assertEqual(recipe.tags.count(), 3)
        self.assertIn(tag, recipe.tags.all())
        for tag in payload['tags']:
            exists = recipe.tags.filter(
                name=tag['name'],
                created_by=self.user
                ).exists()
            self.assertTrue(exists)

    def test_update_recipe_with_tag(self):
        """
        Test update recipe with tags
        """
        recipe = create_recipe(user=self.user)
        payload = {
            'tags': [
                {'name': 'Indian'}
            ]
        }

        url = detail_url(recipe.uuid)
        result = self.client.patch(url, payload, format='json')

        recipe.refresh_from_db()
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        new_tag = Tag.objects.get(created_by=self.user, name='Indian')
        self.assertIn(new_tag, recipe.tags.all())

    def test_recipe_assign_tag(self):
        """
        Test recipe tags assing and removal
        """

        recipe = create_recipe(user=self.user)
        lunch_tag = create_tag(user=self.user, name='Lunch')
        recipe.tags.add(lunch_tag)
        breakfast_tag = create_tag(user=self.user, name='Breakfast')

        payload = {
            'tags': [
                {'name': 'Breakfast'}
            ]
        }

        url = detail_url(recipe.uuid)
        result = self.client.patch(url, payload, format='json')
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertIn(breakfast_tag, recipe.tags.all())
        self.assertNotIn(lunch_tag, recipe.tags.all())

    def test_clear_recipe_tags(self):
        """
        Test recipe clear tags
        """

        recipe = create_recipe(user=self.user)
        lunch_tag = create_tag(user=self.user, name='Lunch')
        breakfast_tag = create_tag(user=self.user, name='Breakfast')
        recipe.tags.add(lunch_tag)
        recipe.tags.add(breakfast_tag)

        payload = {
            'tags': []
        }

        url = detail_url(recipe.uuid)
        result = self.client.patch(url, payload, format='json')

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.tags.count(), 0)

    def test_cerate_recipe_with_ingredient(self):
        """
        Test creating recipe with ingredients
        """
        payload = {
            'title': 'New title',
            'link': 'https://example.com/new',
            'description': 'new',
            'time_minutes': 10,
            'price': Decimal('3.00'),
            'ingredients': [
                {'name': 'Salt'},
                {'name': 'Flower'},
                {'name': 'Butter'}
            ]
        }

        result = self.client.post(RECIPES_URL, payload, format='json')

        self.assertEqual(result.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.filter(created_by=self.user).first()
        self.assertEqual(recipe.created_by, self.user)
        self.assertEqual(recipe.ingredients.count(), 3)
        for ingredient in payload['ingredients']:
            exists = recipe.ingredients.filter(
                name=ingredient['name'],
                created_by=self.user
                ).exists()
            self.assertTrue(exists)

    def test_create_recipe_with_exisiting_ingredient(self):
        """
        Test recipe with exisiting ingredients
        """

        ingredient = create_ingredient(user=self.user, name='Salt')

        payload = {
            'title': 'New title',
            'link': 'https://example.com/new',
            'description': 'new',
            'time_minutes': 10,
            'price': Decimal('3.00'),
            'ingredients': [
                {'name': 'Salt'},
                {'name': 'Flower'},
                {'name': 'Butter'}
            ]
        }

        result = self.client.post(RECIPES_URL, payload, format='json')

        self.assertEqual(result.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.filter(created_by=self.user).first()
        self.assertEqual(recipe.created_by, self.user)
        self.assertEqual(recipe.ingredients.count(), 3)
        self.assertIn(ingredient, recipe.ingredients.all())
        for ingredient in payload['ingredients']:
            exists = recipe.ingredients.filter(
                name=ingredient['name'],
                created_by=self.user
                ).exists()
            self.assertTrue(exists)

    def test_update_recipe_with_ingredient(self):
        """
        Test update recipe with ingredients
        """
        recipe = create_recipe(user=self.user)
        payload = {
            'ingredients': [
                {'name': 'Masala'}
            ]
        }

        url = detail_url(recipe.uuid)
        result = self.client.patch(url, payload, format='json')

        recipe.refresh_from_db()
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        new_ingredient = Ingredient.objects.get(
            created_by=self.user, name='Masala')
        self.assertIn(new_ingredient, recipe.ingredients.all())

    def test_recipe_assign_ingredient(self):
        """
        Test recipe ingredients assing and removal
        """

        recipe = create_recipe(user=self.user)
        rice_ingredient = create_ingredient(user=self.user, name='Rice')
        recipe.ingredients.add(rice_ingredient)
        bread_ingredient = create_ingredient(user=self.user, name='Bread')

        payload = {
            'ingredients': [
                {'name': 'Bread'}
            ]
        }

        url = detail_url(recipe.uuid)
        result = self.client.patch(url, payload, format='json')
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertIn(bread_ingredient, recipe.ingredients.all())
        self.assertNotIn(rice_ingredient, recipe.ingredients.all())

    def test_clear_recipe_ingredients(self):
        """
        Test recipe clear ingredients
        """

        recipe = create_recipe(user=self.user)
        rice_ingredient = create_ingredient(user=self.user, name='Rice')
        bread_ingredient = create_ingredient(user=self.user, name='Bread')
        recipe.ingredients.add(rice_ingredient)
        recipe.ingredients.add(bread_ingredient)

        payload = {
            'ingredients': []
        }

        url = detail_url(recipe.uuid)
        result = self.client.patch(url, payload, format='json')

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.ingredients.count(), 0)
