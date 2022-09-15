"""
User api serializers
"""
from django.contrib.auth import get_user_model
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """
    User object serialzier
    """

    class Meta:
        model = get_user_model()
        fields = ['email', 'password', 'name']
        extra_kwargs = {
            'password': {
                'write_only': True,
                'min_length': 8
            }
        }

    def craete(self, validated_data):
        """
        Create and return a user with encrypted password
        """
        return get_user_model().objects.create_user(**validated_data)
