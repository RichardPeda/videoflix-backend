from django.db import models
from datetime import timedelta
from django.utils.timezone import now
from django.contrib.auth.models import AbstractUser
import uuid 
from django.core.validators import RegexValidator
class CustomUser(AbstractUser):
    """
    Custom user model extending Django's AbstractUser.

    Attributes:
    - is_verified (BooleanField):  
    Indicates whether the user's account has been verified. Defaults to False.

    - username_validator (RegexValidator):  
    Validator enforcing allowed characters in the username: letters, numbers, spaces, and @/./+/-/_.

    - username (CharField):  
    Unique username field with max length 150, using the custom validator.  
    Provides a specific error message if the username is already taken.

    Notes:
    - This model customizes the default Django user by adding verification status and stricter username validation.
    - Ensures usernames only contain permitted characters and prevents duplicates.
    """
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
     """
    Model representing a verification code linked to a specific user.

    Fields:
    - id (UUIDField):  
    Primary key with automatically generated UUID, non-editable.

    - user (OneToOneField):  
    One-to-one relationship to the CustomUser model.  
    Ensures each user has at most one verification code.

    - created_at (DateTimeField):  
    Timestamp automatically set when the record is created.

    Methods:
    - __str__():  
    Returns a string representation combining creation time, user, and UUID.

    Notes:
    - Typically used to manage user account verification or password reset tokens.
    - Guarantees uniqueness and traceability of verification codes per user.
    """

     id = models.UUIDField( 
         primary_key = True, 
         default = uuid.uuid4, 
         editable = False)
     user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
     created_at = models.DateTimeField(auto_now_add=True)

     def __str__(self):
          return f"{self.created_at} {self.user} {self.id}" 
     
class PasswordResetCode(models.Model):
     """
    Model representing a password reset code associated with a specific user.

    Fields:
    - id (UUIDField):  
    Primary key with auto-generated UUID, non-editable.

    - user (OneToOneField):  
    One-to-one relationship to the CustomUser model, linking each code uniquely to a user.

    - created_at (DateTimeField):  
    Automatically set timestamp when the reset code is created.

    Methods:
    - is_valid():  
    Returns True if the reset code is still valid (within 24 hours of creation), False otherwise.

    - __str__():  
    String representation combining creation time, user, and UUID.

    Notes:
    - Used to manage password reset requests securely with expiration logic.
    - Ensures that each user can have only one active reset code at a time.
    """

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