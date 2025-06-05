from django.db import models
from datetime import timedelta
from django.utils.timezone import now
from django.contrib.auth.models import AbstractUser
import uuid 
from django.core.validators import RegexValidator
class CustomUser(AbstractUser):
    is_verified = models.BooleanField(default=False)

    username_validator = RegexValidator(
        regex=r'^[\w.@+\- ]+$',
        message='Enter a valid username. This value may contain only letters, numbers, spaces, and @/./+/-/_ characters.',
    )

    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[username_validator],
        error_messages={
            'unique': "A user with that username already exists.",
        },
    )
class VerifyCode(models.Model):
     id = models.UUIDField( 
         primary_key = True, 
         default = uuid.uuid4, 
         editable = False)
     user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
     created_at = models.DateTimeField(auto_now_add=True)

     def __str__(self):
          return f"{self.created_at} {self.user} {self.id}" 
class PasswordResetCode(models.Model):
     id = models.UUIDField( 
         primary_key = True, 
         default = uuid.uuid4, 
         editable = False)
     user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
     created_at = models.DateTimeField(auto_now_add=True)

     def is_valid(self):
        return now() < self.created_at + timedelta(hours=24)

     def __str__(self):
          return f"{self.created_at} {self.user} {self.id}" 