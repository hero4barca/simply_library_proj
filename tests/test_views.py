import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from library.models import Book, Author, Favorite

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

@pytest.fixture
def create_superuser(db):
    """
    Fixture to create a superuser for authenticated requests.
    """
    return User.objects.create_superuser(username="admin", email="admin@example.com", password="AdminPassword123!")

@pytest.fixture
def create_normal_user(db):
    """
    Fixture to create a normal user for authenticated requests.
    """
    return User.objects.create_user(username="testuser", email="testuser@example.com", password="UserPassword123!")

@pytest.mark.django_db
class TestUserViewSet:
    def setup_method(self):
        self.client = APIClient()


    def test_list_users_as_admin(self, create_superuser):
        """
        Test listing all users as an admin.
        """
        self.client.login(username="admin", password="AdminPassword123!")
        response = self.client.get("/users")
        assert response.status_code == 200
        assert isinstance(response.data['results'], list)  # Expecting a list of users

    def test_list_users_as_normal_user(self,  create_normal_user):
        """
        Test listing all users as a normal user (permission check).
        """
        self.client.login(username="testuser", password="UserPassword123!")
        response = self.client.get("/users")
        assert response.status_code == 200

    def test_retrieve_user(self,  create_normal_user):
        """
        Test retrieving a single user.
        """
        self.client.login(username="testuser", password="UserPassword123!")
        response = self.client.get(f"/users/{create_normal_user.id}")
        assert response.status_code == 200
        assert response.data["username"] == "testuser"
        assert response.data["email"] == "testuser@example.com"

    # def test_create_user_as_admin(self,  create_superuser):
    #     """
    #     Test creating a new user as an admin.
    #     """
    #     self.client.login(username="admin", password="AdminPassword123!")
    #     data = {
    #         "username": "newuser",
    #         "email": "newuser@example.com",
    #         "password": "NewUserPassword123!",
    #     }
    #     response = self.client.post("/users", data=data)
    #     assert response.status_code == 201
    #     assert response.data["username"] == "newuser"
    #     assert response.data["email"] == "newuser@example.com"

@pytest.fixture
def create_test_author(db):
    """
    Fixture to create a test author.
    """
    return Author.objects.create(name="Test Author")

@pytest.fixture
def create_test_books(db, create_test_author):
    """
    Fixture to create test books.
    """
    books = [
        Book.objects.create(title="Book 1", description="Description 1"),
        Book.objects.create(title="Book 2", description="Description 2"),
    ]
    for book in books:
        book.authors.add(create_test_author)
    return books


@pytest.mark.django_db
class TestBookViewSet:
    def setup_method(self):
        self.client = APIClient()

    def test_list_books(self, create_test_books ):
        """
        Test retrieving the list of books.
        """
        response = self.client.get("/books")
        assert response.status_code == 200
        assert len(response.data['results']) == len(create_test_books)


    def test_retrieve_book(self, create_test_books):
        """
        Test retrieving a specific book by ID.
        """
        book = create_test_books[0]
        response = self.client.get(f"/books/{book.id}")
        assert response.status_code == 200
        assert response.data["title"] == book.title
        assert response.data["description"] == book.description


    # def test_create_book(self, create_superuser, create_test_author):
    #     """
    #     Test creating a new book.
    #     """
    #     self.client.login(username="admin", password="AdminPassword123!")
    #     data = {
    #         "title": "New Book",
    #         "description": "New book description",
    #         "authors": [create_test_author.id],
    #     }
    #     response = self.client.post("/books", data=data)
    #     assert response.status_code == 201
    #     assert response.data["title"] == "New Book"