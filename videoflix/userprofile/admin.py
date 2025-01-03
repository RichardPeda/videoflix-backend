from django.contrib import admin

from userprofile.models import UserProfile, Review

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(Review)