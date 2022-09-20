"""
Test for models
"""

from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


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

        user = get_user_model().objects.create_user(
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
            user = get_user_model().objects.create_user(email, 'test_123')
            self.assertEqual(user.email, expected)

    def test_new_user_withou_email_address(self):
        """
        Test user without email, raises value error
        """
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'test_123')

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

        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )

        recipe = models.Recipe.objects.create(
            created_by=user,
            title='Test Recipe',
            time_minutes=5,
            price=Decimal('5.00'),
            description='Description of test recipe',
        )

        self.assertEqual(str(recipe), recipe.title)

