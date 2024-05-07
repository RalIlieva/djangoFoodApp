from django.db import models

# Create your models here.
class Item(models.Model):
    item_name = models.CharField(max_length=200)
    item_desc = models.CharField(max_length=200)
    item_price = models.IntegerField()
    item_image = models.CharField(max_length=550, default='https://cdn-icons-png.flaticon.com/512/1147/1147805.png')

    def __str__(self):
        return self.item_name


