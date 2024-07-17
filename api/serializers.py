from rest_framework import serializers
from food.models import Item, Comment
from users.models import Profile
from django.contrib.auth.models import User

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    # @classmethod
    # def get_token(cls, user):
    #     token = super().get_token(user)
    #     token['name'] = user.username
    #     token['email'] = user.email
    #
    #     return token
    def validate(self, attrs):
        data = super().validate(attrs)

        data['username'] = self.user.username
        data['email'] = self.user.email

        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
        read_only_fields = ['id']
        ref_name = 'ApiUserSerializer'


class ProfileImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading images to profiles"""

    class Meta:
        model = Profile
        fields = ['id', 'image']
        read_only_fields = ['id']
        extra_kwargs = {
            'image': {'required': 'True'},
            'user': {'required': False},
            'location': {'required': False}
        }


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    # image = ProfileImageSerializer

    class Meta:
        model = Profile
        fields = ['user', 'image', 'location']
        read_only_fields = ['id']

    def create(self, validated_data):
        """Create and return a new profile"""
        user_data = validated_data.pop('user')
        user = User.objects.create_user(**user_data)
        profile = Profile.objects.create(user=user, **validated_data)
        return profile

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


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'user', 'item', 'text', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']

    def create(self, validated_data):
        request = self.context.get('request', None)
        if request and request.user:
            validated_data['user'] = request.user
        return super().create(validated_data)


class ItemSerializer(serializers.ModelSerializer):
    user_name = UserSerializer(read_only=True)
    comments = serializers.SerializerMethodField()

    class Meta:
        model = Item
        fields = [
            'id',
            'user_name',
            'item_name',
            'item_desc',
            'item_image',
            'publish_date',
            'update_date',
            'cooking_time',
            'views',
            'comments',
        ]
        read_only_fields = ['id', 'user_name']

    def get_comments(self, obj):
        comments = obj.comments.all()
        return CommentSerializer(comments, many=True).data

    def create(self, validated_data):
        request = self.context.get('request', None)
        if request:
            validated_data['user_name'] = request.user
        return super().create(validated_data)
