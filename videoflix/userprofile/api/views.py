from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from userprofile.api.permissions import IsCustomerCreateReview, IsOwnerOrAdmin, IsReviewerOrAdmin
from userprofile.api.serializers import RegistrationSerializer
from userprofile.models import CustomUser, VerifyCode
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework import generics
# from django_filters.rest_framework import DjangoFilterBackend
# from django_filters import rest_framework as filters

from rest_framework.filters import OrderingFilter
# from django_filters.rest_framework import DjangoFilterBackend
# from drf_spectacular.utils import extend_schema, extend_schema_serializer, inline_serializer
from rest_framework import serializers
from ..tasks import send_email_to_user



class LoginView(ObtainAuthToken):
    
    def post(self, request, *args, **kwargs):
        """
        Authenticates a user and returns an authentication token that is used for further API requests.

        Args:
            request (auth.user): Only authenticated users

        Returns:
            JSON: Response with token, user id, email and username.
        """
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        # profile = UserProfile.objects.get(user=user)
        token, created = Token.objects.get_or_create(user=user)
        # return Response({
        #     'token': token.key,
        #     'user_id': profile.pk,
        #     'email': user.email,
        #     'username' : user.username
        # }, status=status.HTTP_200_OK)

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        """
        A POST-request compares the given passwords and if the user or the email already exists.
        This API provides endpoints for user login and registration.
        Login provides the user with a token for authentication and registration creates a new user,
        automatically assigning a customer or business user profile.
        The function returns a JSON when is was successfull.

        Args:
            request (data): username: Username of the new user. Email: Email address of the new user.
	        Password: Password for the new user. Repeated_password: Repetition of the password for confirmation.
	        Type: Profile type (business or customer profile).

        Returns:
            JSON: Response with token, user id, email and username.
        """
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            saved_account = serializer.save()
            code, created = VerifyCode.objects.get_or_create(user=saved_account)
           
            send_email_to_user.delay(user_id=saved_account.id, code=code.id)

            return Response({
            'message': 'verification email was sent'
            }, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
