from django.conf import settings
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from django.urls import reverse
from userprofile.models import CustomUser, PasswordResetCode, VerifyCode
import uuid
from unittest.mock import patch

from userprofile.tasks import send_password_reset_email_to_user, send_verification_email_to_user
from unittest.mock import patch, MagicMock
from django.test import RequestFactory, TestCase

from userprofile.api.permissions import IsOwnerOrAdmin

class LoginOrSignupTest(APITestCase):
    """
    API test case for the login or signup endpoint.

    Setup:
    - Creates a test user with username 'testuser' and email 'test@test.de'.
    - Sets a password for the user.
    - Defines the URL for the login-signup endpoint.

    Test Methods:
    - test_existing_user_returns_user_exists():
    Sends a POST request with an existing user's email.
    Expects HTTP 200 and response message 'user exists' along with the email.

    - test_nonexistent_user_returns_user_does_not_exist():
    Sends a POST request with a non-existing email.
    Expects HTTP 200 and response message 'user does not exist' without an email in response.

    - test_missing_email_returns_bad_request():
    Sends a POST request without an email.
    Expects HTTP 400 Bad Request and response message 'wrong information'.

    Purpose:
    - Verifies the behavior of the login/signup endpoint for various input scenarios.
    - Ensures correct responses for existing users, new users, and invalid requests.
    """

    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create(username='testuser', email='test@test.de')
        self.user.set_password('testuser')
        self.url = reverse('login-signup')

    def test_existing_user_returns_user_exists(self):
        data = {'email': 'test@test.de'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'user exists')
        self.assertEqual(response.data['email'], 'test@test.de')

    def test_nonexistent_user_returns_user_does_not_exist(self):
        data = {'email': 'newuser@test.de'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'user does not exist')
        self.assertNotIn('email', response.data)

    def test_missing_email_returns_bad_request(self):
        data = {}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'wrong information')

class LoginUserTest(APITestCase):
    """
    API test case for the user login endpoint.

    Setup:
    - Creates a verified and active test user with username 'test_user_name' and email 'test@test.de'.
    - Sets the user's password.
    - Defines the URL for the login endpoint.

    Test Methods:
    - test_login_user_success():
    Sends a POST request with correct email and password.
    Expects HTTP 200 OK indicating successful login.

    - test_login_wrong_password():
    Sends a POST request with correct email but wrong password.
    Expects HTTP 401 Unauthorized.

    - test_login_nonexistent_user():
    Sends a POST request with an email that does not exist.
    Expects HTTP 401 Unauthorized.

    Purpose:
    - Validates the login endpoint's behavior for successful and failed authentication attempts.
    - Ensures proper status codes for correct and incorrect login credentials.
    """

    def setUp(self):
        self.client = APIClient()  
        self.user = CustomUser.objects.create(username='test_user_name', email='test@test.de')
        self.user.set_password('testuser')
        self.user.is_verified = True
        self.user.is_active = True
        self.user.save()
        self.url = reverse('login')

    def test_login_user_success(self):
        
        data = {'email': 'test@test.de', 'password' : 'testuser'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_wrong_password(self):
        data = {'email': 'test@test.de', 'password': 'wrongpassword'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_nonexistent_user(self):
        data = {'email': 'doesnotexist@test.de', 'password': 'testuser'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class RegisterViewTest(APITestCase):
    """
    API test case for the user registration endpoint.

    Setup:
    - Initializes the test client and sets the registration URL.

    Test Methods:
    - test_successful_registration():
    Sends a POST request with valid registration data.
    Verifies that the response status is 200 OK.
    Checks that a verification email task was triggered.
    Confirms that the new user exists in the database.

    - test_password_mismatch():
    Sends a POST request with mismatched password and repeated_password.
    Expects HTTP 400 Bad Request.
    Validates the error message indicating password mismatch.

    - test_existing_username_and_email():
    Creates an existing user.
    Sends a POST request with duplicate username and email.
    Expects HTTP 400 Bad Request.
    Checks that the response contains username validation errors.

    - test_missing_fields():
    Sends a POST request with empty data.
    Expects HTTP 400 Bad Request.
    Verifies that validation errors are returned for all required fields.

    Purpose:
    - Ensures the registration endpoint correctly handles user creation, validations, and error cases.
    - Confirms that verification email is sent upon successful registration.
    """

    def setUp(self):
        self.client = APIClient()
        self.url = reverse('register')

    @patch('userprofile.tasks.send_verification_email_to_user.delay')
    def test_successful_registration(self, mock_send_email):
        data = {
            'username': 'newuser',
            'email': 'newuser@test.de',
            'password': 'testpassword123',
            'repeated_password': 'testpassword123',
            'type': 'customer'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'verification email was sent')
        self.assertTrue(CustomUser.objects.filter(email='newuser@test.de').exists())
        self.assertTrue(mock_send_email.called)

    def test_password_mismatch(self):
        data = {
            'username': 'testuser',
            'email': 'testuser@test.de',
            'password': 'abc123',
            'repeated_password': 'def456'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)
        self.assertEqual(response.data['password'], ['Das Passwort ist nicht gleich mit dem wiederholten Passwort'])

    def test_existing_username_and_email(self):
        self.user = CustomUser.objects.create_user(username='existinguser', email='exist@test.de')
        self.user.set_password('abc123')
        data = {
            'username': 'existinguser',
            'email': 'exist@test.de',
            'password': 'testpass',
            'repeated_password': 'testpass'
        }
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

    def test_missing_fields(self):
        data = {}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)
        self.assertIn('email', response.data)
        self.assertIn('password', response.data)
        self.assertIn('repeated_password', response.data)

class VerificationViewTest(APITestCase):
    """
    API test case for the user email verification endpoint.

    Setup:
    - Creates a test user with inactive and unverified status.
    - Generates a verification code associated with the user.
    - Sets the verification URL.

    Test Methods:
    - test_successful_verification():
    Sends a POST request with valid user_id and verification code.
    Expects HTTP 200 OK with a success message.
    Checks that the user's is_verified and is_active flags are set to True.
    Confirms that the verification code is deleted after successful verification.

    - test_invalid_code():
    Sends a POST request with a valid user_id but an invalid (nonexistent) verification code.
    Expects HTTP 404 Not Found.

    - test_invalid_user():
    Sends a POST request with an invalid (nonexistent) user_id and a valid verification code.
    Expects HTTP 404 Not Found.

    - test_missing_fields():
    Sends a POST request without required fields.
    Expects HTTP 404 Not Found.

    Purpose:
    - Ensures the verification endpoint properly validates the user and code.
    - Confirms user activation and cleanup of verification codes after success.
    - Handles invalid input scenarios gracefully.
    """

    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(username='verifyuser', email='verify@test.de', password='123test', is_active=False, is_verified=False)
        self.code = VerifyCode.objects.create(user=self.user)
        self.url = reverse('verification')

    def test_successful_verification(self):
        data = {
            'user_id': self.user.id,
            'code': self.code.id
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'user verified')

        self.user.refresh_from_db()
        self.assertTrue(self.user.is_verified)
        self.assertTrue(self.user.is_active)
        self.assertFalse(VerifyCode.objects.filter(id=self.code.id).exists())

    def test_invalid_code(self):
        invalid_code = uuid.uuid4() 
        data = {
            'user_id': self.user.id,
            'code': str(invalid_code)
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_invalid_user(self):
        data = {
            'user_id': 9999,
            'code': self.code.id
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_missing_fields(self):
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class PasswordResetInquiryTest(APITestCase):
    """
    API test case for the password reset inquiry endpoint.

    Setup:
    - Creates a test user with email and password.
    - Sets the inquiry URL.

    Test Methods:
    - test_existing_email_sends_email():
    Sends a POST request with an existing user's email.
    Expects HTTP 200 OK with a generic success message.
    Verifies that the password reset email task is called.

    - test_nonexistent_email_returns_success():
    Sends a POST request with an email not registered in the system.
    Expects HTTP 200 OK with the same generic success message.
    Verifies that no email task is called (to avoid leaking user existence).

    - test_missing_email_returns_error():
    Sends a POST request without the 'email' field.
    Expects HTTP 400 Bad Request with an error message stating the email is required.

    Purpose:
    - Ensures the password reset inquiry endpoint always responds safely without leaking user existence.
    - Validates proper error handling for missing data.
    """

    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(username='testuser', email='test@example.com', password='secure123')
        self.url = reverse('password-reset-inquiry')

    @patch('userprofile.tasks.send_password_reset_email_to_user.delay')
    def test_existing_email_sends_email(self, mock_send_email):
        response = self.client.post(self.url, {'email': 'test@example.com'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'If an account with that email exists, a reset email was sent.')
        self.assertTrue(mock_send_email.called)

    @patch('userprofile.tasks.send_password_reset_email_to_user.delay')
    def test_nonexistent_email_returns_success(self, mock_send_email):
        response = self.client.post(self.url, {'email': 'nonexistent@example.com'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'If an account with that email exists, a reset email was sent.')
        self.assertFalse(mock_send_email.called)

    def test_missing_email_returns_error(self):
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Email is required')

class PasswordResetTest(APITestCase):
    """
    API test case for the password reset endpoint.

    Setup:
    - Creates a test user with an initial password.
    - Creates a PasswordResetCode linked to that user.
    - Sets the URL for password reset.

    Test Methods:
    - test_successful_password_reset():
    Sends a POST request with valid user ID, reset code, and matching new passwords.
    Expects HTTP 200 OK with success message.
    Verifies the user's password is updated and the reset code is deleted.

    - test_password_mismatch():
    Sends a POST request where the new password and repeated password do not match.
    Expects HTTP 400 Bad Request with an error message about password mismatch.

    - test_invalid_code():
    Sends a POST request with a valid user ID but an invalid reset code.
    Expects HTTP 400 Bad Request with an error message about invalid code or user.

    - test_missing_fields():
    Sends a POST request without required fields.
    Expects HTTP 400 Bad Request with an error indicating all fields are required.

    Purpose:
    - To verify the password reset endpoint correctly handles valid and invalid input,
    enforces password matching, and cleans up reset codes after successful resets.
    """

    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(username='resetuser', email='reset@example.com', password='oldpass123')
        self.code = PasswordResetCode.objects.create(user=self.user)
        self.url = reverse('password-reset')

    def test_successful_password_reset(self):
        data = {
            'user_id': self.user.id,
            'code': str(self.code.id),
            'password': 'newpassword123',
            'repeated_password': 'newpassword123'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], 'Password reset successful')
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpassword123'))
        self.assertFalse(PasswordResetCode.objects.filter(id=self.code.id).exists())

    def test_password_mismatch(self):
        data = {
            'user_id': self.user.id,
            'code': str(self.code.id),
            'password': 'newpass',
            'repeated_password': 'differentpass'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Passwords do not match.')

    def test_invalid_code(self):
        invalid_uuid = uuid.uuid4()
        data = {
            'user_id': self.user.id,
            'code': str(invalid_uuid),
            'password': 'somepass',
            'repeated_password': 'somepass'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], 'Invalid reset code or user.')

    def test_missing_fields(self):
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], 'All fields are required.')


class SendVerificationEmailTest(TestCase):
    """
    Tests the send_verification_email_to_user task.

    Setup:
    - Creates a test user.
    - Sets a dummy verification code.

    Test:
    - Mocks the Django EmailMessage class and the render_to_string function.
    - Calls the task with the test user ID and code.
    - Asserts that the email template is rendered.
    - Asserts the EmailMessage is constructed with correct subject, body, sender, and recipient.
    - Asserts that the email's send() method is called once.
    """

    def setUp(self):
        self.user = CustomUser.objects.create_user(username='verifyuser', email='verify@test.com', password='test123')
        self.code = 1234

    @patch('userprofile.tasks.EmailMessage')
    @patch('userprofile.tasks.render_to_string', return_value='<p>test html</p>')
    def test_send_verification_email(self, mock_render, mock_email_class):
        mock_email_instance = MagicMock()
        mock_email_class.return_value = mock_email_instance

        send_verification_email_to_user(code=self.code, user_id=self.user.id)

        mock_render.assert_called_once()
        mock_email_class.assert_called_once_with(
            subject="Confirm your email",
            body='<p>test html</p>',
            from_email=settings.EMAIL_FROM,
            to=[self.user.email]
        )
        mock_email_instance.send.assert_called_once()

class SendPasswordResetEmailTest(TestCase):
    """
    Tests the send_password_reset_email_to_user task.

    Setup:
    - Creates a test user and sets a dummy reset code.
    - Uses the FRONTEND_BASEURL from settings as part of the email context.

    Test:
    - Mocks the EmailMessage class and the render_to_string function.
    - Calls the task with the test user ID and reset code.
    - Verifies the correct email template is rendered with the expected context.
    - Checks the EmailMessage is created with the right subject, body, sender, and recipient.
    - Confirms the email's send() method is called once.
    """

    def setUp(self):
        self.user = CustomUser.objects.create_user(username='resetuser', email='reset@test.com', password='reset123')
        self.code = 5678
        self.url = settings.FRONTEND_BASEURL

    @patch('userprofile.tasks.EmailMessage')
    @patch('userprofile.tasks.render_to_string', return_value='<p>reset email html</p>')
    def test_send_password_reset_email(self, mock_render, mock_email_class):
        mock_email_instance = MagicMock()
        mock_email_class.return_value = mock_email_instance
        send_password_reset_email_to_user(code=self.code, user_id=self.user.id)

        mock_render.assert_called_once_with(
            'emails/reset_password_email.html',
            context={'user_id': self.user.id, 'code': self.code, 'url': self.url}
        )

        mock_email_class.assert_called_once_with(
            subject="Reset your Password",
            body='<p>reset email html</p>',
            from_email=settings.EMAIL_FROM,
            to=[self.user.email]
        )

        mock_email_instance.send.assert_called_once()


class IsOwnerOrAdminTest(TestCase):
    """
    Tests for the IsOwnerOrAdmin permission class.

    - SAFE_METHODS (GET, HEAD, OPTIONS) should allow any user.
    - Owner of the object has permission for all methods.
    - Admin (superuser) has permission for all methods.
    - Other users are denied access for non-safe methods.
    """
    def setUp(self):
        self.factory = RequestFactory()
        self.owner = CustomUser.objects.create_user(username='owner', email='owner@test.com', password='pass')
        self.other = CustomUser.objects.create_user(username='other', email='other@test.com', password='pass')
        self.admin = CustomUser.objects.create_superuser(username='admin', email='admin@test.com', password='pass')
        self.permission = IsOwnerOrAdmin()

    def test_safe_method_allows_anyone(self):
        request = self.factory.get('/')
        request.user = self.other
        self.assertTrue(self.permission.has_object_permission(request, None, self.owner))

    def test_owner_has_permission(self):
        request = self.factory.post('/')
        request.user = self.owner
        self.assertTrue(self.permission.has_object_permission(request, None, self.owner))

    def test_admin_has_permission(self):
        request = self.factory.put('/')
        request.user = self.admin
        self.assertTrue(self.permission.has_object_permission(request, None, self.owner))

    def test_other_user_denied(self):
        request = self.factory.delete('/')
        request.user = self.other
        self.assertFalse(self.permission.has_object_permission(request, None, self.owner))
