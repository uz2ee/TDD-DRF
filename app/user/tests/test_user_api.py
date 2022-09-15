"""
Test for user
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
JWT_TOKEN_CREATE_URL = reverse('user:token-create')
JWT_TOKEN_REFRESH_URL = reverse('user:token-refresh')


def create_user(**params):
    """
    Create and returns a new user
    """
    return get_user_model().objects.create_user(**params)


class PublicUserAPITests(TestCase):
    """
    Test the public featuers of the user API.
    """

    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        """
        Test create user success
        """
        payload = {
            'email': 'test@example.com',
            'password': 'test__pass',
            'name': 'Test',
        }

        result = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(result.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', result.data)

    def test_user_with_email_exisit(self):
        """
        Test if user can be created with existing created user email
        """
        payload = {
            'email': 'test@example.com',
            'password': 'test__pass',
            'name': 'Test',
        }
        create_user(**payload)
        result = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)

    def test_pasword_length(self):
        """
        Test minimum password length
        """
        payload = {
            'email': 'test@example.com',
            'password': 'pws',
            'name': 'Test',
        }
        result = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
            ).exists()
        self.assertFalse(user_exists)

    def test_create_jwt_for_user(self):
        """
        Test JWT token create
        """
        payload = {
            'email': 'test@example.com',
            'password': 'test__pass',
            'name': 'Test'
        }
        create_user(**payload)
        payload = {
            'email': 'test@example.com',
            'password': 'test__pass'
        }
        result = self.client.post(JWT_TOKEN_CREATE_URL, payload)
        self.assertIn('access', result.data)
        self.assertIn('refresh', result.data)
        self.assertEqual(result.status_code, status.HTTP_200_OK)


    def test_refresh_jwt_for_user(self):
        """
        Test JWT token create
        """
        payload = {
            'email': 'test@example.com',
            'password': 'test__pass',
            'name': 'Test'
        }
        create_user(**payload)
        payload = {
            'email': 'test@example.com',
            'password': 'test__pass'
        }
        result = self.client.post(JWT_TOKEN_CREATE_URL, payload)
        refresh_token = result.data['refresh']
        payload = {
            'refresh': refresh_token
        }
        result = self.client.post(JWT_TOKEN_REFRESH_URL, payload)

        self.assertIn('access', result.data)
        self.assertEqual(result.status_code, status.HTTP_200_OK)