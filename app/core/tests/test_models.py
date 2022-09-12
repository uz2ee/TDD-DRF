"""
Test for models
"""

from django.test import TestCase
from django.contrib.auth import get_user_model


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
            ['Test2@Example.com', 'Test@example.com'],
            ['TEST3@EXAMPLE>COM', 'TEST3@example.com'],
            ['test4@example.COM', 'Test4@example.com'],
        ]
        for email, expected in samlple_emails:
            user = get_user_model().objects.create_user(email, 'test_123')
            self.assertEqual(user.email, expected)

