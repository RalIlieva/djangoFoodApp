from django.test import TestCase
from django.contrib.auth.models import User
from datetime import timedelta
from .models import Item
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


