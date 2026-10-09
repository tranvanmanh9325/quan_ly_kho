from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token


class AuthAPITestCase(APITestCase):
    """
    Test suite for Authentication endpoints:
    - POST /api/v1/auth/register/
    - POST /api/v1/auth/login/
    - GET /api/v1/auth/me/
    """

    def setUp(self):
        super().setUp()
        self.username = 'activeuser'
        self.password = 'StrongPass123@'
        self.user = User.objects.create_user(
            username=self.username,
            password=self.password,
            email='active@example.com',
            first_name='Active',
            last_name='User'
        )
        self.token = Token.objects.create(user=self.user)

    def test_register_user_success_201(self):
        # Verify valid registration creates user and returns HTTP 201 Created with token
        payload = {
            "username": "newuser",
            "password": "Password123@",
            "email": "newuser@example.com",
            "first_name": "New",
            "last_name": "User"
        }
        response = self.client.post('/api/v1/auth/register/', payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user']['username'], "newuser")
        self.assertTrue(bool(response.data['token']))
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_register_user_missing_password_400(self):
        # Verify registration without password returns HTTP 400 Bad Request
        payload = {
            "username": "nopassuser",
            "email": "nopass@example.com"
        }
        response = self.client.post('/api/v1/auth/register/', payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)

    def test_register_user_duplicate_username_400(self):
        # Verify duplicate username returns HTTP 400 Bad Request
        payload = {
            "username": self.username,
            "password": "Password123@",
            "email": "duplicate@example.com"
        }
        response = self.client.post('/api/v1/auth/register/', payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_user_success_200(self):
        # Verify valid credentials returns HTTP 200 OK and token
        payload = {
            "username": self.username,
            "password": self.password
        }
        response = self.client.post('/api/v1/auth/login/', payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['token'], self.token.key)
        self.assertEqual(response.data['user']['username'], self.username)

    def test_login_invalid_credentials_400(self):
        # Verify incorrect password returns HTTP 400 Bad Request
        payload = {
            "username": self.username,
            "password": "WrongPassword999@"
        }
        response = self.client.post('/api/v1/auth/login/', payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_inactive_user_400(self):
        # Verify disabled account returns HTTP 400 Bad Request
        self.user.is_active = False
        self.user.save()

        payload = {
            "username": self.username,
            "password": self.password
        }
        response = self.client.post('/api/v1/auth/login/', payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_profile_authenticated_200(self):
        # Verify authenticated request to /me/ returns HTTP 200 OK and profile details
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.get('/api/v1/auth/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.username)
        self.assertEqual(response.data['email'], 'active@example.com')

    def test_get_profile_unauthenticated_401(self):
        # Verify unauthenticated request to /me/ returns HTTP 401 Unauthorized
        self.client.credentials()  # Clear credentials
        response = self.client.get('/api/v1/auth/me/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_register_user_short_password_400(self):
        # Password with length < 6 must be rejected with HTTP 400 Bad Request
        payload = {
            "username": "shortpassuser",
            "password": "123",
            "email": "shortpass@example.com"
        }
        response = self.client.post('/api/v1/auth/register/', payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)

    def test_login_missing_fields_400(self):
        # Login payload missing password must be rejected with HTTP 400 Bad Request
        payload = {
            "username": self.username
        }
        response = self.client.post('/api/v1/auth/login/', payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)

