from django.contrib import admin

from .models import CustomUser, VerifyCode, PasswordResetCode

admin.site.register(CustomUser)
admin.site.register(VerifyCode)
admin.site.register(PasswordResetCode)
