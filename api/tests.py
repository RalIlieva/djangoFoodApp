"""
Create tests for the API.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from food.models import Item, Comment
from users.models import Profile
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('api-register')
# PROFILE_URL = reverse('profile')

class PublicUserApiTests(TestCase):
    """Test public features of the public API."""

    def setUp(self):
        self.client = APIClient()

    def test_create_user_successful(self):
        """Test creating a user is successful."""
        payload = {
            'username': 'example',
            'email': 'test@example.com',
            'password1': '1234567890',
            'password2': '1234567890'
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        user_exists = User.objects.filter(
            username=payload['username']
        ).exists()
        self.assertTrue(user_exists)
