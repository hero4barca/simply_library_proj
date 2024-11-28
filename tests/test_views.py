import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User

@pytest.mark.django_db
class TestRegisterView():
    def setup_method(self):
        self.client = APIClient()
        self.register_url = '/api/register'

    def test_register_user_success(self):
        # Test successful registration with valid data
        payload = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "StrongPassword123!"
        }
        response = self.client.post(self.register_url, data=payload)

        # Assertions
        assert response.status_code == 201  # HTTP_201_CREATED
        assert response.data['detail'] == "User registered successfully"
        assert User.objects.filter(username="testuser").exists()

    def test_register_user_missing_fields(self):
        # Test registration with missing fields
        payload = {
            "username": "testuser",
            "password": "StrongPassword123!"
        }

        with pytest.raises(KeyError) as excinfo:
            response = self.client.post(self.register_url, data=payload)

        # Assertions
        assert "email" in str(excinfo.value)  # Missing email field error

    def test_register_user_invalid_email(self):
        # Test registration with an invalid email format
        payload = {
            "username": "testuser",
            "email": "invalid-email",
            "password": "StrongPassword123!"
        }
        response = self.client.post(self.register_url, data=payload)

        # Assertions
        assert response.status_code == 400  # HTTP_400_BAD_REQUEST
        assert "email" in response.data  # Email validation error


    def test_register_user_short_password(self):
        # Test registration with a password that is too short
        payload = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "123"
        }
        response = self.client.post(self.register_url, data=payload)

        # Assertions
        assert response.status_code == 400  # HTTP_400_BAD_REQUEST
        assert "password" in response.data  # Password validation error

    def test_register_user_duplicate_username(self):
        # Test registration with a duplicate username
        User.objects.create_user(username="testuser", email="testuser@example.com", password="StrongPassword123!")
        payload = {
            "username": "testuser",
            "email": "newemail@example.com",
            "password": "AnotherStrongPassword123!"
        }
        response = self.client.post(self.register_url, data=payload)

        # Assertions
        assert response.status_code == 400  # HTTP_400_BAD_REQUEST
        assert "username" in response.data  # Duplicate username error

    def test_register_user_duplicate_email(self):
        # Test registration with a duplicate email
        User.objects.create_user(username="existinguser", email="testuser@example.com", password="StrongPassword123!")
        payload = {
            "username": "newuser",
            "email": "testuser@example.com",
            "password": "AnotherStrongPassword123!"
        }
        response = self.client.post(self.register_url, data=payload)

        # Assertions
        assert response.status_code == 400  # HTTP_400_BAD_REQUEST
        assert "email" in response.data  # Duplicate email error


@pytest.fixture
def create_user(db):
    """
    Fixture to create a test user for login tests.
    """
    return User.objects.create_user(username="testuser", email="testuser@example.com", password="StrongPassword123!")

@pytest.mark.django_db
class TestLoginView():

    def setup_method(self):
        self.client = APIClient()
        self.login_url = '/api/login'

    def test_login_valid_credentials(self, create_user):
        """
        Test logging in with valid credentials.
        """
        data = {
            "username": "testuser",
            "password": "StrongPassword123!",
        }
        response = self.client.post(self.login_url, data=data)
        assert response.status_code == 200
        assert "access" in response.data
        assert "refresh" in response.data


    def test_login_invalid_password(self, create_user):
        """
        Test logging in with an invalid password.
        """
        data = {
            "username": "testuser",
            "password": "WrongPassword!",
        }
        response = self.client.post(self.login_url, data=data)
        assert response.status_code == 401
        assert "access" not in response.data
        assert "refresh" not in response.data
        assert response.data["detail"] == "No active account found with the given credentials"


    def test_login_invalid_username(self, create_user):
        """
        Test logging in with an invalid username.
        """
        data = {
            "username": "invaliduser",
            "password": "StrongPassword123!",
        }
        response = self.client.post(self.login_url , data=data)
        assert response.status_code == 401
        assert "access" not in response.data
        assert "refresh" not in response.data
        assert response.data["detail"] == "No active account found with the given credentials"

    def test_login_missing_password(self , create_user):
        """
        Test logging in with a missing password field.
        """
        data = {
            "username": "testuser",
        }
        response = self.client.post(self.login_url, data=data)
        assert response.status_code == 400
        assert "access" not in response.data
        assert "refresh" not in response.data
        assert "password" in response.data

    def test_login_missing_username(self, create_user):
        """
        Test logging in with a missing username field.
        """
        data = {
            "password": "StrongPassword123!",
        }
        response = self.client.post(self.login_url, data=data)
        assert response.status_code == 400
        assert "access" not in response.data
        assert "refresh" not in response.data
        assert "username" in response.data

    def test_login_inactive_user(self):
        """
        Test logging in with an inactive user.
        """
        inactive_user = User.objects.create_user(username="inactiveuser", password="StrongPassword123!", is_active=False)
        data = {
            "username": "inactiveuser",
            "password": "StrongPassword123!",
        }
        response = self.client.post(self.login_url, data=data)
        assert response.status_code == 401
        assert "access" not in response.data
        assert "refresh" not in response.data
        assert response.data["detail"] == "No active account found with the given credentials"
