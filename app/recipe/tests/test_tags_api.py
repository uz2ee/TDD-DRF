"""
Test for tag apis
"""


from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Tag

from recipe.serializers import (
    TagSerializer,
)

from core.tests.test_models import (
    create_user,
    create_tag,
)

TAGS_URL = reverse('recipe:tag-list')


def detail_url(tag_uuid):
    """
    Create and return a tag details url
    """
    return reverse('recipe:tag-detail', args=[tag_uuid])


class PublicTagAPITests(TestCase):
    """
    Test public tag apis
    """

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """
        Test retrieve tags
        """
        result = self.client.get(TAGS_URL)

        self.assertEqual(result.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagAPITests(TestCase):
    """
    Test authenticated tag apis
    """

    def setUp(self):
        self.user = create_user(
            email='test@example.com',
            password='test_password',
            name='Test Name'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_tag(self):
        """
        Test retrieve tag list
        """
        create_tag(user=self.user, name="Veg")
        create_tag(user=self.user, name="Non-Veg")

        result = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data, serializer.data)

    def test_retrieve_user_limited_tag_list(self):
        """
        Test retrieve tag list
        """

        self.other_user = create_user(
            email='test2@example.com',
            password='test2_password',
            name='Test Name 2'
        )
        create_tag(self.user)
        create_tag(self.user)
        create_tag(self.other_user)
        create_tag(self.other_user)

        result = self.client.get(TAGS_URL)

        tags = Tag.objects.filter(created_by=self.user).order_by('-name')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data, serializer.data)

    def test_patch_tag(self):
        """
        Test tag update
        """

        tag = create_tag(
            user=self.user,
            name='Sample name'
        )
        payload = {
            'name': 'New name'
        }
        url = detail_url(tag.uuid)
        result = self.client.patch(url, payload)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload['name'])
        self.assertEqual(tag.created_by, self.user)
        self.assertEqual(tag.updated_by, self.user)

    def test_put_tag(self):
        """
        Test tag update
        """

        tag = create_tag(
            user=self.user,
            name='Sample name'
        )
        payload = {
            'name': 'New name'
        }
        url = detail_url(tag.uuid)
        result = self.client.put(url, payload)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload['name'])
        self.assertEqual(tag.created_by, self.user)
        self.assertEqual(tag.updated_by, self.user)

    def test_put_tag_unsecssful(self):
        """
        Test tag update fail correctly for missing params
        """
        tag = create_tag(
            user=self.user,
            name='Sample Name'
        )
        payload = {}

        url = detail_url(tag.uuid)
        result = self.client.put(url, payload)

        self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_tag_unsecssful(self):
        """
        Test tag update user fail correctly
        """
        tag = create_tag(
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

        url = detail_url(tag.uuid)
        result = self.client.put(url, payload)

        self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_tag(self):
        """
        Test delete tag
        """
        tag = create_tag(user=self.user)

        url = detail_url(tag.uuid)
        result = self.client.delete(url)

        self.assertEqual(result.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Tag.objects.filter(uuid=tag.uuid).exists())

    def test_delete_tag_of_other_user(self):
        """
        Test delete tag of other users
        """
        new_user = create_user(
            email='test2@example.com',
            password='test2_password',
            name='Test Name 2'
        )
        tag = create_tag(user=new_user)

        url = detail_url(tag.uuid)
        result = self.client.delete(url)

        self.assertEqual(result.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Tag.objects.filter(uuid=tag.uuid).exists())
