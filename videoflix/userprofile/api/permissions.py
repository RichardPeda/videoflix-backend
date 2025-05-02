from rest_framework.permissions import BasePermission, SAFE_METHODS
from userprofile.models import CustomUser

class IsOwnerOrAdmin(BasePermission):
    
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        else:
            user= CustomUser.objects.get(username=request.user)
            return bool(user==obj or request.user.is_superuser)

