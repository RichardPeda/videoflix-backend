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

        # Refresh user from db and check flags
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_verified)
        self.assertTrue(self.user.is_active)

        # Check that code is deleted
        self.assertFalse(VerifyCode.objects.filter(id=self.code.id).exists())

    def test_invalid_code(self):
        invalid_code = uuid.uuid4()  # creates valid but not existing uuid
        data = {
            'user_id': self.user.id,
            'code': str(invalid_code)
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_invalid_user(self):
        data = {
            'user_id': 9999,  # not existing user
            'code': self.code.id
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_missing_fields(self):
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)




class PasswordResetInquiryTest(APITestCase):

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
        self.assertFalse(mock_send_email.called)  # kein tatsächlicher Versand

    def test_missing_email_returns_error(self):
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Email is required')

class PasswordResetTest(APITestCase):

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

# 

class SendVerificationEmailTest(TestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(username='verifyuser', email='verify@test.com', password='test123')
        self.code = 1234  # Beispielcode

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
