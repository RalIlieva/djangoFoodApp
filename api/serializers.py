from rest_framework import serializers
from food.models import Item, Comment
from users.models import Profile
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
        ref_name = 'ApiUserSerializer'

class ProfileImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading images to profiles"""

    class Meta:
        model = Profile
        fields = ['id', 'image']
        read_only_fields = ['id']
        extra_kwargs = {'image': {'required': 'True'}}


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Profile
        fields = ['user', 'image', 'location']

    def update(self, instance, validated_data):
        """Partial update of the user profile"""
        user_data = validated_data.pop('user', None)
        user = instance.user


        # Update user fields
        if user_data:
            for attr, value in user_data.items():
                setattr(user, attr, value)
            user.save()

        # Update profile fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance


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
