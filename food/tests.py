from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import timedelta
from .models import Item, Comment
from .forms import CommentForm, ItemForm
from star_ratings.models import Rating
from django.contrib.contenttypes.models import ContentType

class IndexViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_user = User.objects.create_user(username='testuser', password='testpass')
        cls.item1 = Item.objects.create(
            item_name='Pizza',
            item_desc='Cheesy pizza',
            cooking_time=timedelta(minutes=30),
            user_name=cls.test_user,
        )
        cls.item2 = Item.objects.create(
            item_name='Burger',
            item_desc='Juicy burger',
            cooking_time=timedelta(minutes=20),
            user_name=cls.test_user,
        )
        # Create ratings for item1 and item2
        content_type = ContentType.objects.get_for_model(Item)

        # Create rating for item1
        cls.rating1 = Rating.objects.create(
            content_type=content_type,
            object_id=cls.item1.id,
            average=5,
            count=1
        )

        # Create rating for item2
        cls.rating2 = Rating.objects.create(
            content_type=content_type,
            object_id=cls.item2.id,
            average=4,
            count=1
        )

    def test_view_url_exists_at_proper_location(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'food/index.html')

    def test_lists_all_items(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Pizza')
        self.assertContains(response, 'Burger')


    def test_pagination_is_three(self):
        response = self.client.get('/')
        self.assertLessEqual(len(response.context['item_list']), 3)

    def test_search_functionality(self):
        response = self.client.get('/?q=Pizza')
        self.assertContains(response, 'Pizza')

    def test_search_no_results(self):
        response = self.client.get('/?q=Sushi')
        self.assertNotContains(response, 'Pizza')
        self.assertNotContains(response, 'Burger')


class FoodDetailViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_user = User.objects.create_user(username='testuser', password='testpass')
        cls.item1 = Item.objects.create(
            item_name='Pizza',
            item_desc='Cheesy pizza',
            cooking_time=timedelta(minutes=30),
            user_name=cls.test_user,
        )
        cls.comment1 = Comment.objects.create(
            item=cls.item1,
            user=cls.test_user,
            text='Delicious!',
        )
        # Create rating for item1
        content_type = ContentType.objects.get_for_model(Item)
        cls.rating1 = Rating.objects.create(
            content_type=content_type,
            object_id=cls.item1.id,
            average=5,
            count=1
        )

    def test_view_url_exists_at_proper_location(self):
        response = self.client.get(f'/{self.item1.pk}/')
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('food:detail', kwargs={'pk': self.item1.pk}))
        self.assertTemplateUsed(response, 'food/detail.html')

    def test_context_data_contains_comments_and_form(self):
        response = self.client.get(reverse('food:detail', kwargs={'pk': self.item1.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertIn('comments', response.context)
        self.assertIn('comment_form', response.context)
        self.assertEqual(len(response.context['comments']), 1)
        self.assertIsInstance(response.context['comment_form'], CommentForm)

    def test_view_count_increments(self):
        initial_views = self.item1.views
        self.client.get(reverse('food:detail', kwargs={'pk': self.item1.pk}))
        self.item1.refresh_from_db()
        self.assertEqual(self.item1.views, initial_views + 1)

    def test_post_comment_valid(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('food:detail', kwargs={'pk': self.item1.pk}), {
            'text': 'New Comment',
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Comment.objects.filter(item=self.item1).count(), 2)

    def test_post_comment_invalid(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('food:detail', kwargs={'pk': self.item1.pk}), {
            'text': ''  # Invalid because content is required
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'comment_form', 'text', 'This field is required.')


class CreateItemViewTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.url = reverse('food:create_item')
        self.valid_item_data = {
            'item_name': 'Test Item',
            'item_desc': 'Test description',
            'item_image': 'https://cdn-icons-png.flaticon.com/512/1147/1147805.png',
            'cooking_time': timedelta(minutes=30),
        }

    def test_create_item_get(self):
        # Test GET request to the view
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'food/item-form.html')
        # Verify the form is present in the response context
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], ItemForm)

        # Check if the rendered HTML contains the form fields
        self.assertContains(response, 'name="item_name"')
        self.assertContains(response, 'name="item_desc"')
        self.assertContains(response, 'name="item_image"')
        self.assertContains(response, 'name="cooking_time"')

    def test_create_item_post_valid(self):
        # Test POST request with valid data
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(self.url, self.valid_item_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Item.objects.filter(item_name='Test Item').exists())


    def test_create_item_post_invalid(self):
        # Test POST request with invalid data
        self.client.login(username='testuser', password='testpass')
        invalid_item_data = self.valid_item_data.copy()
        invalid_item_data['item_name'] = ''  # Make it invalid by providing empty item_name
        response = self.client.post(self.url, invalid_item_data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Item.objects.filter(item_name='').exists())
        self.assertContains(response, 'This field is required.')

    def test_create_item_without_login(self):
        # Test creating item without being logged in
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/login/?next={self.url}')