from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from userprofile.api.serializers import RegistrationSerializer
from userprofile.models import CustomUser, VerifyCode, PasswordResetCode
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework import status
from ..tasks import send_password_reset_email_to_user, send_verification_email_to_user

class LoginOrSignupView(APIView):
    def post(self, request):
        """
        Checks whether a user with the given email exists in the system.

        This endpoint is used as a preliminary step for login or signup flows. 
        It does not authenticate or register a user, but simply verifies existence based on the email.

        Args:
            request (Request): POST request with JSON body containing 'email' field.

        Returns:
            Response (JSON):
                - 200 OK:
                    If user exists:
                        {
                            "message": "user exists",
                            "email": "user@example.com"
                        }
                    If user does not exist:
                        {
                            "message": "user does not exist"
                        }
                - 400 Bad Request:
                    If 'email' is missing from the request:
                        {
                            "message": "wrong information"
                        }
        """

        email = request.data.get('email')

        if(email is not None):
            try:
                user = CustomUser.objects.get(email=email)
                return Response(data={'message' : 'user exists', 'email' : user.email}, status=status.HTTP_200_OK)
            except:
                return Response(data={'message' : 'user does not exist'}, status=status.HTTP_200_OK)
        else:
            return Response(data={'message' : 'wrong information'}, status=status.HTTP_400_BAD_REQUEST)

class LoginView(ObtainAuthToken):
    
    def post(self, request, *args, **kwargs):
        """
        Authenticates a user and returns an authentication token that is used for further API requests.

        Args:
            request (auth.user): Only authenticated users

        Returns:
            JSON: Response with token, user id and email.
        """
        email = request.data.get('email')
        password = request.data.get('password')
        
        try:
            user = CustomUser.objects.get(email=email)
            if user.check_password(password):
                if user.is_verified and user.is_active:
                    token, created = Token.objects.get_or_create(user=user)
                    return Response({
                        'token': token.key,
                        'user_id': user.pk,
                        'email': user.email,
                    }, status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_401_UNAUTHORIZED)

        except:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
             
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Registers a new user and initiates the email verification process.

        This endpoint creates a new user account if the submitted data is valid.
        After registration, it generates a verification code and sends it via email asynchronously.

        Args:
            request (Request): POST request with user registration data (defined in RegistrationSerializer).

        Returns:
            Response (JSON):
                - 200 OK:
                    {
                        "message": "verification email was sent"
                    }
                - 400 Bad Request:
                    {
                        "field_name": ["error message"],
                        ...
                    }
                    Returned if the submitted data is invalid, with detailed serializer error messages.
        """

        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            saved_account = serializer.save()
            code, created = VerifyCode.objects.get_or_create(user=saved_account)
           
            send_verification_email_to_user.delay(user_id=saved_account.id, code=code.id)

            return Response({
            'message': 'verification email was sent'
            }, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerificationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Verifies a user's email using a verification code.

        This endpoint activates a user account if the provided verification code is valid.
        Once verified, the user is marked as active and the verification code is deleted.

        Args:
            request (Request): POST request with JSON body containing:
                - user_id (int): ID of the user to verify
                - code (int): Verification code ID assigned to the user

        Returns:
            Response (JSON):
                - 200 OK:
                    {
                        "message": "user verified"
                    }
                - 404 Not Found:
                    Returned if the verification code is invalid or does not match the user.
        """

        req_user_id = request.data.get('user_id')
        req_code = request.data.get('code')

        try:
            code = VerifyCode.objects.get(user=req_user_id, id=req_code)
            user = code.user
            user.is_verified = True
            user.is_active = True
            user.save()
            code.delete()
            
            return Response({'message' : 'user verified'}, status=status.HTTP_200_OK)
        except VerifyCode.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

class PasswordResetInquiryView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        """
        Initiates a password reset process by sending a reset email to the user.

        This endpoint accepts an email address and, if a matching user is found, generates a password reset code 
        and sends an email asynchronously. For security reasons, the response is the same regardless of whether 
        the email exists in the system.

        Args:
            request (Request): POST request with JSON body containing:
                - email (str): Email address of the user requesting password reset

        Returns:
            Response (JSON):
                - 200 OK:
                    {
                        "message": "If an account with that email exists, a reset email was sent."
                    }
                - 400 Bad Request:
                    {
                        "error": "Email is required"
                    }
        """
      
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(email=email)
            code, created = PasswordResetCode.objects.get_or_create(user=user)
            send_password_reset_email_to_user.delay(user_id=user.pk, code=code.id)
        except CustomUser.DoesNotExist:
            pass # Intentionally no error message → Protection against hackers
        # Uniform response - even if the e-mail does not exist
        return Response({'message': 'If an account with that email exists, a reset email was sent.'}, status=status.HTTP_200_OK)
        
class PasswordReset(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Resets a user's password using a valid reset code.

        This endpoint verifies a password reset code and allows the user to set a new password.
        It ensures all fields are present, validates the reset code, and checks password confirmation before applying changes.

        Args:
            request (Request): POST request with JSON body containing:
                - user_id (int): ID of the user requesting password reset
                - code (int): Password reset code ID
                - password (str): New password
                - repeated_password (str): Confirmation of the new password

        Returns:
            Response (JSON):
                - 200 OK:
                    {
                        "message": "Password reset successful"
                    }
                - 400 Bad Request:
                    If fields are missing:
                    {
                        "error": "All fields are required."
                    }
                    If passwords do not match:
                    {
                        "error": "Passwords do not match."
                    }
                    If reset code or user is invalid:
                    {
                        "error": "Invalid reset code or user."
                    }
        """

        user_id = request.data.get('user_id')
        code_id = request.data.get('code')
        pw = request.data.get('password')
        repeated_pw = request.data.get('repeated_password')

        if not all([user_id, code_id, pw, repeated_pw]):
            return Response({'error': 'All fields are required.'}, status=status.HTTP_400_BAD_REQUEST)

        if pw != repeated_pw:
            return Response({'error': 'Passwords do not match.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            code = PasswordResetCode.objects.get(user=user_id, id=code_id)
        except PasswordResetCode.DoesNotExist:
            return Response({'error': 'Invalid reset code or user.'}, status=status.HTTP_400_BAD_REQUEST)

        user = code.user
        user.set_password(pw)
        user.save()
        code.delete()

        return Response({'message': 'Password reset successful'}, status=status.HTTP_200_OK)