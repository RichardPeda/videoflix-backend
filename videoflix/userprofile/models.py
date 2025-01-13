from django.db import models
import datetime
from django.contrib.auth.models import AbstractUser
import uuid 




# Create your models here.
class CustomUser(AbstractUser):
    is_verified = models.BooleanField(default=False)
   
    

class VerifyCode(models.Model):
     id = models.UUIDField( 
         primary_key = True, 
         default = uuid.uuid4, 
         editable = False)
     user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
     created_at = models.DateTimeField(auto_now_add=True)

     def __str__(self):
          return f"{self.created_at} {self.user} {self.id}" 

