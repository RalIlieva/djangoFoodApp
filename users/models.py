import uuid
import os
from django.db import models
from django.contrib.auth.models import User


def upload_to(instance, filename):
    """Generate file path for new user image."""
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'
    return os.path.join('profile_pictures', filename)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='profilepic.jpg', upload_to=upload_to)
    location = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username
