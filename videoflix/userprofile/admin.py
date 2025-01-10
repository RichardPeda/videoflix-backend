from django.contrib import admin

from .models import CustomUser, VerifyCode

admin.site.register(CustomUser)
admin.site.register(VerifyCode)
