from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.contenttypes.fields import GenericRelation
from star_ratings.models import Rating

# Create your models here.
class Item(models.Model):
    user_name = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    item_name = models.CharField(max_length=200)
    item_desc = models.CharField(max_length=200)
    item_price = models.IntegerField()
    item_image = models.CharField(max_length=550, default='https://cdn-icons-png.flaticon.com/512/1147/1147805.png')
    ratings = GenericRelation(Rating, related_query_name='items')
    def get_absolute_url(self):
        return reverse('food:detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.item_name


