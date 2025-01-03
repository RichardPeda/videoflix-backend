from rest_framework.permissions import BasePermission, SAFE_METHODS
from userprofile.models import UserProfile

class IsOwnerOrAdmin(BasePermission):
    
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        else:
            user= UserProfile.objects.get(user=request.user)
            return bool(user==obj or request.user.is_superuser)


class IsCustomerCreateReview(BasePermission):
    
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        if request.method == 'POST':
            user= UserProfile.objects.get(user=request.user)
            return bool(request.user and user.type == 'customer')
            

class IsReviewerOrAdmin(BasePermission):
    
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            print(obj.reviewer)
            print(request.user)
            return True
        else:
            user= UserProfile.objects.get(user=request.user)
            return bool(user==obj.reviewer or request.user.is_superuser)
