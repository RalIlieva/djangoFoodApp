"""
Create tests for the API.
"""
import tempfile
import os
from PIL import Image
from django.test import TestCase
from django.contrib.auth.models import User
from food.models import Item, Comment
from users.models import Profile
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from api.serializers import UserSerializer, ProfileSerializer, ProfileImageSerializer

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
            'user': {
                'email': 'newmail@example.com'
            },
            'location': 'new location'
        }
        profile_url = reverse('profile-detail', args=[self.user.profile.id])
        res = self.client.patch(profile_url, payload, format='json')

        self.user.refresh_from_db()
        self.assertEqual(self.user.email, payload['user']['email'])
        self.assertEqual(self.user.profile.location, payload['location'])
        self.assertEqual(res.status_code, status.HTTP_200_OK)


class ImageUploadTests(TestCase):
    """Tests for the image upload API."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            username='example',
            email='example@example.com',
            password='testpass123',
        )
        self.client.force_authenticate(self.user)


    def tearDown(self):
        self.user.profile.image.delete()

    def test_upload_image(self):
        """Test uploading an image to a profile user."""
        url = reverse('upload-image', args=[self.user.profile.id])
        with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:
            img = Image.new('RGB', (10, 10))
            img.save(image_file, format='JPEG')
            image_file.seek(0)
            payload = {'image': image_file}
            res = self.client.post(url, payload, format='multipart')

        self.user.profile.refresh_from_db()
        if res.status_code != status.HTTP_200_OK:
            print(res.content)  # Print response content for debugging
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.user.profile.image.path))
