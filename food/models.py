from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.contenttypes.fields import GenericRelation
from star_ratings.models import Rating
from django.utils import timezone

# Create your models here.
class Item(models.Model):
    user_name = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    item_name = models.CharField(max_length=200)
    item_desc = models.CharField(max_length=200)
    item_image = models.CharField(max_length=550, default='https://cdn-icons-png.flaticon.com/512/1147/1147805.png')
    ratings = GenericRelation(Rating, related_query_name='items')
    publish_date = models.DateTimeField(default=timezone.now)
    update_date = models.DateTimeField(auto_now=True)
    cooking_time = models.DurationField()
    views = models.PositiveIntegerField(default=0)
    def get_absolute_url(self):
        return reverse('food:detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.item_name


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.user.username} on {self.item.item_name}'
