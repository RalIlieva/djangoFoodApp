# Generated by Django 4.2 on 2024-05-07 19:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('food', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='item_image',
            field=models.CharField(default='https://cdn-icons-png.flaticon.com/512/1147/1147805.png', max_length=550),
        ),
    ]
