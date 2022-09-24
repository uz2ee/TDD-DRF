"""
Test for user app
Including JWT
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.tests.test_models import create_user

CREATE_USER_URL = reverse('user:create')
JWT_TOKEN_CREATE_URL = reverse('user:token-create')
JWT_TOKEN_REFRESH_URL = reverse('user:token-refresh')
JWT_TOKEN_VERIFY_URL = reverse('user:token-verify')
USER_URL = reverse('user:self')


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

    def test_user_with_email_exist(self):
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

    def test_password_length(self):
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

    def test_create_jwt_for_user_success(self):
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

    def test_create_jwt_for_user_fail(self):
        """
        Test JWT token create
        """
        payload = {
            'email': 'test@example.com',
            'password': 'wrong__pass'
        }
        result = self.client.post(JWT_TOKEN_CREATE_URL, payload)
        self.assertEqual(result.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_jwt_for_user_success(self):
        """
        Test JWT token refresh
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

    def test_refresh_jwt_for_user_fail(self):
        """
        Test JWT token refresh
        """
        payload = {
            'refresh': 'wrong_token'
        }
        result = self.client.post(JWT_TOKEN_REFRESH_URL, payload)

        self.assertNotIn('access', result.data)
        self.assertEqual(result.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_verify_jwt_for_user_success(self):
        """
        Test JWT token verify
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
        access_token = result.data['access']
        payload = {
            'token': access_token
        }
        result = self.client.post(JWT_TOKEN_VERIFY_URL, payload)

        self.assertEqual(result.status_code, status.HTTP_200_OK)

    def test_verify_jwt_for_user_fail(self):
        """
        Test JWT token verify
        """
        payload = {
            'token': 'wrong_access'
        }
        result = self.client.post(JWT_TOKEN_VERIFY_URL, payload)

        self.assertEqual(result.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_user_unauthorizzed(self):
        """
        Test retrieve self details
        """
        result = self.client.get(USER_URL)

        self.assertEqual(result.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserAPITests(TestCase):
    """
    Test authenticated apis
    """

    def setUp(self):
        self.user = create_user(
            email='test@example.com',
            password='test_password',
            name='Test Name'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """
        Test retrieve self details
        """
        result = self.client.get(USER_URL)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data, {
            'name': self.user.name,
            'email': self.user.email
        })

    def test_post_not_allowed_on_self_profile_update(self):
        """
        Test post is not allowed in profile
        """

        result = self.client.post(USER_URL, {})

        self.assertEqual(
            result.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """
        Test update user profile test
        """
        payload = {
            'password': 'test__pass',
            'name': 'Updated Name'
        }
        result = self.client.patch(USER_URL, payload)

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(self.user.name, payload['name'])
        self.assertEqual(result.status_code, status.HTTP_200_OK)
