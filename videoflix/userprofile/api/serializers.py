from rest_framework import serializers
from userprofile.models import Review, UserProfile
from django.contrib.auth.models import User
import datetime


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['pk','first_name', 'last_name', 'username']

class UserFlattenSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField('get_alternate_name')
    class Meta:
        model = User
        fields = ['user','first_name', 'last_name', 'username', 'email']
        
    def get_alternate_name(self, obj):
        """
        Only the primary key is returned and not the whole user
        """
        return obj.pk
    
    
class UserGetProfileSerializer(serializers.ModelSerializer):
    user = UserFlattenSerializer()
    class Meta:
        model = UserProfile
        exclude = ['id', 'uploaded_at']
    
    def to_representation(self, obj):
        """
        Move fields from profile to user as representation.
        """
        representation = super().to_representation(obj)
        profile_representation = representation.pop('user')
        for key in profile_representation:
            representation[key] = profile_representation[key]
        return representation
    
    def update(self, instance, validated_data):
        """
        Updates the Userprofile partial with the existing fields and save it.
        """
        instance.user.first_name = self.context['request'].POST.get('first_name', instance.user.first_name)
        instance.user.last_name = self.context['request'].POST.get('last_name', instance.user.last_name)
        instance.user.email = self.context['request'].POST.get('email', instance.user.email)
        instance.user.save()
        
        instance.file = validated_data.get('file', instance.file)
        instance.location = validated_data.get('location', instance.location)
        instance.tel = validated_data.get('tel', instance.tel)
        instance.description = validated_data.get('description', instance.description)
        instance.working_hours = validated_data.get('working_hours', instance.working_hours)
        instance.save()
        return instance

class BusinessUserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = UserProfile
        exclude = ['id', 'created_at', 'uploaded_at']

    def update(self, instance, validated_data):
        """
        Update of the business user. Partial update is allowed.
        """
        user_data = validated_data.pop('user', None)
        if user_data is not None:
            serializer = UserSerializer(instance.user, data=user_data, partial=True)
            if serializer.is_valid():
                serializer.save()           
        return instance
    
class CustomerUserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = UserProfile
        exclude = ['id', 'location', 'tel','description', 'working_hours', 'created_at']
        
    def update(self, instance, validated_data):
        """
        Update of the customer user. Partial update is allowed.
        """
        user_data = validated_data.pop('user', None)
        if user_data is not None:
            serializer = UserSerializer(instance.user, data=user_data, partial=True)
            if serializer.is_valid():
                serializer.save()           
        return instance
    
    
class GetUserOffersSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = UserProfile
        fields = '__all__'
        
    def to_representation(self, obj):
        """
        Change the representation of the user. The field user will be removed.
        """
        representation = super().to_representation(obj)
        user = representation.pop('user')
        return ({
            'first_name' : user['first_name'],
            'last_name' : user['last_name'],
            'username' : user['username'],
        })


class ReviewSerializer(serializers.ModelSerializer):
    reviewer = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = Review
        fields = '__all__'
    
class SingleReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ['business_user', 'reviewer','created_at', 'updated_at']
    
    
        
    

class RegistrationSerializer(serializers.ModelSerializer):
    repeated_password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
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
        """
        Save a new user after the validation of the fields.
        """
        pw = self.validated_data['password']
        email = self.validated_data['email']
        username = self.validated_data['username']        
        account = User(email=email, username=username)
        account.set_password(pw)
        account.save()
        return account