from rest_framework import serializers
from food.models import Item, Comment
from users.models import Profile
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
        ref_name = 'ApiUserSerializer'

class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Profile
        fields = ['user', 'image', 'location']

class ItemSerializer(serializers.ModelSerializer):
    user_name = UserSerializer()

    class Meta:
        model = Item
        fields = ['id', 'user_name', 'item_name', 'item_desc', 'item_image', 'publish_date', 'update_date', 'cooking_time', 'views']

class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    item = ItemSerializer()

    class Meta:
        model = Comment
        fields = ['id', 'user', 'item', 'text', 'created_at']
