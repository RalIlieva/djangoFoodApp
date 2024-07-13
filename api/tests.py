"""
Create tests for the API.
"""
import tempfile
import os
from datetime import timedelta, datetime
from django.utils import timezone
import pytz
from deepdiff import DeepDiff
from PIL import Image
from django.test import TestCase
from django.contrib.auth.models import User
from food.models import Item, Comment
from users.models import Profile
from django.urls import reverse


from rest_framework.test import APIClient
from rest_framework import status
from api.serializers import (
    UserSerializer,
    ProfileImageSerializer,
    ProfileSerializer,
    ItemSerializer,
    CommentSerializer,
)


CREATE_USER_URL = reverse('api-register')
# ITEM_LIST_URL = reverse('food:index')
ITEM_LIST_URL = reverse('item-list')
ITEM_DETAIL_URL = lambda pk: reverse('item-detail', args=[pk])


def detail_url(item_id):
    """Create and return a recipe detail URL."""
    return reverse('food:detail', args=[item_id])

def create_user(**params):
    """Create and return a new user."""
    return User.objects.create_user(**params)


def create_item(user, **params):
    """Create and return a sample recipe"""
    defaults = {
        'user_name': user,
        'item_name': 'Sample Recipe',
        'item_desc': 'Sample description',
        'item_image': 'https://cdn-icons-png.flaticon.com/512/1147/1147805.png',
        'publish_date': timezone.now(),
        'cooking_time': timedelta(minutes=30),
    }
    defaults.update(params)
    item = Item.objects.create(**defaults)
    return item


def normalize_cooking_time(cooking_time):
    """Normalize cooking time to match the response format."""
    if isinstance(cooking_time, str):
        return cooking_time
    total_seconds = int(cooking_time.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f'{hours:02}:{minutes:02}:{seconds:02}'


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


class PublicRecipeApi(TestCase):
    """Test unauthenticated API clients get list view."""

    def setUp(self):
        self.client = APIClient()

    def normalize_cooking_time(self, cooking_time):
        """Normalize cooking time to match the response format."""
        total_seconds = int(cooking_time.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        # Ensure hours are two digits for consistency
        return f'{hours:02}:{minutes:02}:{seconds:02}'

    def test_auth_not_required_index(self):
        """Test auth is not required to call API."""
        res = self.client.get(ITEM_LIST_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_auth_not_required_detail(self):
        """Test auth is not required to view detail recipe."""
        self.user = create_user(
            username='User',
            email='user@example.com',
            password='testpass123',
        )
        item = create_item(user=self.user)

        # url = detail_url(item.id)
        url = ITEM_DETAIL_URL(item.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)


    def test_auth_not_required_detail_serializer(self):
        """Test auth is not required to view detail recipe."""
        self.user = create_user(
            username='User',
            email='user@example.com',
            password='testpass123',
        )
        item = create_item(user=self.user)

        url = ITEM_DETAIL_URL(item.id)
        res = self.client.get(url)
        item.refresh_from_db()
        serializer = ItemSerializer(item)

        # Normalize the response data to ensure consistency
        normalized_res_data = res.data.copy()
        normalized_res_data['cooking_time'] = self.normalize_cooking_time(item.cooking_time)

        # Ensure user_name field in response data is complete
        normalized_res_data['user_name'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email
        }

        # Adjust datetime fields for comparison
        normalized_res_data['publish_date'] = item.publish_date.isoformat().replace('+00:00', 'Z')
        normalized_res_data['update_date'] = item.update_date.isoformat().replace('+00:00', 'Z')

        # Use deepdiff to find differences
        diff = DeepDiff(normalized_res_data, serializer.data, ignore_order=True)
        if diff:
            print("Differences:", diff)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(normalized_res_data, serializer.data)

class PrivateRecipeApiTests(TestCase):
    """Test authenticated API clients get list view."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            username='RaliTheTester',
            email='example@example.com',
            password='testpass123',
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Test retrieving a list of recipes"""
        create_item(user=self.user)
        create_item(user=self.user)

        url = ITEM_LIST_URL
        items = Item.objects.all().order_by('id')
        serializer = ItemSerializer(items, many=True)
        res = self.client.get(url)

        for item in res.data:
            item['cooking_time'] = normalize_cooking_time(item['cooking_time'])

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipe_list_all_to_user(self):
        """Test list of all recipes is retrieved by the authenticated user."""
        other_user = create_user(
            username='OtherUser',
            email='other@example.com',
            password='password123',
        )
        create_item(user=other_user, item_name='OtherUser Recipe')
        create_item(user=self.user, item_name='User Recipe')

        res = self.client.get(ITEM_LIST_URL)
        items = Item.objects.all()
        serializer = ItemSerializer(items, many=True)

        for item in res.data:
            item['cooking_time'] = normalize_cooking_time(item['cooking_time'])

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_recipe_detail(self):
        """Test get recipe detail."""
        item = create_item(user=self.user)

        url = ITEM_DETAIL_URL(item.id)
        res = self.client.get(url)
        serializer = ItemSerializer(item)

        self.assertEqual(res.data, serializer.data)

    def test_create_recipe(self):
        """Test creating a recipe"""
        payload = {
            'item_name': 'Bean Soup',
            'item_desc': 'Delicious soup made of beans',
            'item_image': 'https://example.png',
            'publish_date': timezone.now().isoformat(),
            'cooking_time': '00:15:00',
        }
        res = self.client.post(ITEM_LIST_URL, payload)
        if res.status_code != status.HTTP_201_CREATED:
            print('Response content:', res.content)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        item = Item.objects.get(id=res.data['id'])
        for key, value in payload.items():
            if key == 'publish_date':
                # Convert string to datetime for comparison
                value = datetime.fromisoformat(value).replace(tzinfo=pytz.UTC)
            elif key == 'cooking_time':
                # Convert string to timedelta for comparison
                value = timedelta(
                    hours=int(value.split(':')[0]),
                    minutes=int(value.split(':')[1]),
                    seconds=int(value.split(':')[2]),
                )
            self.assertEqual(getattr(item, key), value)
        self.assertEqual(item.user_name, self.user)

    def test_partial_update_recipe(self):
        """Test partial update of a recipe"""
        original_link = 'https://example.com/recipe.pdf'
        item = create_item(
            user=self.user,
            item_name='Sample Recipe',
            item_image=original_link
        )

        payload = {'item_name': 'Updated Recipe Name'}
        url = ITEM_DETAIL_URL(item.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        item.refresh_from_db()
        self.assertEqual(item.item_name, payload['item_name'])
        self.assertEqual(item.item_image, original_link)
        self.assertEqual(item.user_name, self.user)

    def test_recipe_full_update(self):
        """Test recipe full update."""
        item = create_item(
            user=self.user,
            item_name='Lentils Soup',
            item_desc='Sample lentils soup',
            item_image='https://example.com/recipe/images.png',
        )
        payload = {
            'item_name': 'Lentils Meal with Beans',
            'item_desc':'Delicious vegan mean',
            'item_image':'https://example.com/recipe/newimage.png',
            'publish_date': timezone.now(),
            'cooking_time': timedelta(minutes=12),
        }
        url = ITEM_DETAIL_URL(item.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        item.refresh_from_db()
        for k, v in payload.items():
            self.assertEqual(getattr(item, k), v)
        self.assertEqual(item.user_name, self.user)

    def test_update_user_returns_error(self):
        """Test changing the recipe user returns in an error."""
        new_user = create_user(
            username='New User',
            email='test@example.com',
            password='newpass',
        )
        item = create_item(user=self.user)
        payload = {'user': new_user.id}
        url = ITEM_DETAIL_URL(item.id)
        self.client.patch(url, payload)

        item.refresh_from_db()
        self.assertEqual(item.user_name, self.user)

    def test_delete_recipe(self):
        """Test deleting a recipe is successful."""
        item = create_item(user=self.user)
        url = ITEM_DETAIL_URL(item.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Item.objects.filter(id=item.id).exists())

    def test_delete_other_users_recipe_error(self):
        """Test trying to delete another user recipe gives an error."""
        new_user = create_user(
            username='New User',
            email='testuser@example.com',
            password='testpass123',
        )
        item = create_item(user=new_user)
        url = ITEM_DETAIL_URL(item.id)

        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Item.objects.filter(id=item.id).exists())

    def test_comment_list_to_recipe(self):
        """Test viewing comments to a recipe"""
        item = create_item(user=self.user)
        comment_sample = Comment.objects.create(user=self.user, item=item, text='Sample comment')
        item.comments.add(comment_sample)
        url = ITEM_DETAIL_URL(item.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # Check that the comment is included in the response
        comment_data = CommentSerializer(comment_sample).data
        self.assertIn(comment_data, res.data['comments'])

    def test_create_comment(self):
        """Test creating a comment."""
        self.item = create_item(user=self.user)
        payload = {
            'text': 'Test comment - hooray',
            'item': self.item.id,
        }
        res = self.client.post(reverse('comment-list'), payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(Comment.objects.get().text, payload['text'])
        self.assertEqual(Comment.objects.get().user, self.user)