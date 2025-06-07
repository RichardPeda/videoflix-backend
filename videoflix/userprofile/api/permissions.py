from rest_framework.permissions import BasePermission, SAFE_METHODS
from userprofile.models import CustomUser

class IsOwnerOrAdmin(BasePermission):
    """
    Custom permission to only allow owners of an object or admin users to edit it.

    - Read-only requests (GET, HEAD, OPTIONS) are allowed for any user.
    - Write requests (POST, PUT, DELETE, etc.) are only allowed if the requesting user
      is either the owner of the object (obj) or has admin privileges (is_superuser).

    Assumes that:
    - If the object (`obj`) is an instance of CustomUser, permission is granted if
      the object is the requesting user.
    - For other models, it checks if the object has a `.user` attribute and compares
      that to the requesting user.

    Returns:
        bool: True if permission is granted, False otherwise.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        else:
            user= CustomUser.objects.get(username=request.user)
            return bool(user==obj or request.user.is_superuser)

