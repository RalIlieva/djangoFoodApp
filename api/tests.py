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
# PROFILE_URL = reverse('profile-detail')


def create_user(**params):
    """Create and return a new user."""
    return User.objects.create_user(**params)

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


class PrivateUserAPITest(TestCase):
    """Test API that require authentication"""

    def setUp(self):
        self.user = create_user(
            username='example',
            email='example@example.com',
            password='testpass123',
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """Test retrieving profile for logged in users."""
        profile_url = reverse('profile-detail', args=[self.user.profile.id])
        res = self.client.get(profile_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'user': {
                'id': self.user.id,
                'username': self.user.username,
                'email': self.user.email,
            },
            'image': f'http://testserver{self.user.profile.image.url}',
            'location': self.user.profile.location,
        })

    def test_update_user_profile(self):
        """Test updating user profile"""
        payload = {
            'user': {''
                     'email': 'newmail@example.com'
                     }

        }
        profile_url = reverse('profile-detail', args=[self.user.profile.id])
        res = self.client.patch(profile_url, payload, format='json')

        self.user.refresh_from_db()
        self.assertEqual(self.user.email, payload['user']['email'])
