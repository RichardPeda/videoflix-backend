from rest_framework import serializers
# from django.contrib.auth.models import User
from ..models import CustomUser
import datetime





    
  
        
    

class RegistrationSerializer(serializers.ModelSerializer):
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

        print(data)
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
        """
        Save a new user after the validation of the fields.
        """

        print(self)
        pw = self.validated_data['password']
        email = self.validated_data['email']
        username = self.validated_data['username']        
        account = CustomUser(email=email, username=username, is_active=False, is_verified=False)
        account.set_password(pw)
        account.save()
        return account