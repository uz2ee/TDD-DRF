"""
Test for models
"""

from unittest.mock import patch
from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model

from core.models import (
    Recipe,
    Tag,
    Ingredient,
)
from core.models import recipe_image_file_path


def create_user(**params):
    """
    Create and returns a new user
    """
    return get_user_model().objects.create_user(**params)


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


def create_tag(user, **params):
    """
    Create and return a new tag
    """
    return Tag.objects.create(created_by=user, **params)


def create_ingredient(user, **params):
    """
    Create and return a new ingredient
    """
    return Ingredient.objects.create(created_by=user, **params)


class ModelTests(TestCase):
    """
    Test models
    """
    def test_create_user_with_email_ok(self):
        """
        Test creating user with email
        """
        email = 'test@example.com'
        password = 'test_pass'

        user = create_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """
        Test email is normalized for new users
        """
        samlple_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['Test4@example.COM', 'Test4@example.com'],
        ]
        for email, expected in samlple_emails:
            user = create_user(email=email, password='test_123')
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_address(self):
        """
        Test user without email, raises value error
        """
        with self.assertRaises(ValueError):
            create_user(email='', password='test_123')

    def test_create_superuser(self):
        """
        Test creating superuser
        """
        email = 'test@example.com'
        password = 'test_pass'

        user = get_user_model().objects.create_superuser(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_recpie_create(self):
        """
        Test creating recipe
        """
        email = 'test@example.com'
        password = 'test_pass'

        user = create_user(
            email=email,
            password=password,
        )

        recipe = create_recipe(
            user=user,
            title='Test Recipe',
            time_minutes=5,
            price=Decimal('5.00'),
            description='Description of test recipe',
        )

        self.assertEqual(str(recipe), recipe.title)

    def test_tag_create(self):
        """
        Test creating tag
        """
        email = 'test@example.com'
        password = 'test_pass'

        user = create_user(
            email=email,
            password=password,
        )

        tag = create_tag(
            user=user,
            name='Test Tag'
        )

        self.assertEqual(str(tag), tag.name)

    def test_ingredient_create(self):
        """
        Test creating ingredient
        """
        email = 'test@example.com'
        password = 'test_pass'

        user = create_user(
            email=email,
            password=password,
        )

        ingredient = create_ingredient(
            user=user,
            name='Test Ingredient'
        )

        self.assertEqual(str(ingredient), ingredient.name)

    @patch('core.models.uuid.uuid4')
    def test_recipe_file_name_uuid(self, mock_uuid):
        """
        Test generating image path
        """
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = recipe_image_file_path(None, 'example.jpg')

        self.assertEqual(file_path, f'uploads/recipe/{uuid}.jpg')
