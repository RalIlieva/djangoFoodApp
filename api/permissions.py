from rest_framework import permissions
from food.models import Item, Comment

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit or delete it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD, or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the object.
        if isinstance(obj, Item):
            return obj.user_name == request.user
        elif isinstance(obj, Comment):
            return obj.user == request.user
        return False
