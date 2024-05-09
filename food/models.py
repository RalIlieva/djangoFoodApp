from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Item(models.Model):
    user_name = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    item_name = models.CharField(max_length=200)
    item_desc = models.CharField(max_length=200)
    item_price = models.IntegerField()
    item_image = models.CharField(max_length=550, default='https://cdn-icons-png.flaticon.com/512/1147/1147805.png')

    def __str__(self):
        return self.item_name


