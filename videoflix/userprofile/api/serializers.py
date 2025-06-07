from rest_framework import serializers
from ..models import CustomUser
import datetime
from django.contrib.auth import authenticate


class RegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for registering a new user.

    Validates that:
    - The username is unique (case-insensitive).
    - The email is unique (case-insensitive).
    - The password and repeated_password match.

    On save, creates a new CustomUser instance with the provided data,
    sets the password securely, and initializes the user as inactive and unverified.

    Fields:
        - username: The desired username (unique).
        - email: The user's email address (unique).
        - password: The user's password (write-only).
        - repeated_password: Confirmation of the password (write-only).
    """
    email = serializers.EmailField(required=True)
    repeated_password = serializers.CharField(write_only=True)
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'repeated_password']
        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }
            
    def validate(self, data):
        """
        Validation of different fields.
        The username must not yet exist.
        The email must not yet exist.
        The password and the repeaded_passwords must match.
        """
        errors = {}
        username = data.get("username")
        if self.Meta.model.objects.filter(username__iexact=username).exists():
           errors["username"] ="Dieser Benutzername ist bereits vergeben"
           
        email = data.get("email")
        if self.Meta.model.objects.filter(email__iexact=email).exists():
           errors["email"] ="Diese E-Mail-Adresse wird bereits verwendet"

        pw = data.get("password")
        repeated_pw = data.get("repeated_password")
        
        if pw != repeated_pw:
            errors["password"] ="Das Passwort ist nicht gleich mit dem wiederholten Passwort"
        
        if errors:
            raise serializers.ValidationError(errors)
        return data
    
    def save(self):
        pw = self.validated_data['password']
        email = self.validated_data['email']
        username = self.validated_data['username']        
        account = CustomUser(email=email, username=username, is_active=False, is_verified=False)
        account.set_password(pw)
        account.save()
        return account
    
