import pytest
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from django.urls import reverse
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


@pytest.mark.django_db
class TestUserViewSet:

    def test_list_users_as_admin(self, authenticated_client_as_admin):
        """
        Test listing all users as an admin.
        """
        response = authenticated_client_as_admin.get("/users")
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data['results'], list)  # Expecting a list of users

    def test_list_users_permission_denied_for_non_admin(self, authenticated_client_as_user):
        """
        Test that a non-admin user gets a 403 Forbidden when trying to list all users.
        """
        response = authenticated_client_as_user.get("/users")
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data["detail"] == "You do not have permission to perform this action."

    def test_retrieve_own_user_details(self, authenticated_client_as_user, create_normal_user):
        """
        Test that a user can retrieve their own details.
        """
        response = authenticated_client_as_user.get(f"/users/{create_normal_user.id}")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["username"] == create_normal_user.username

    def test_retrieve_other_user_details_as_non_admin(self, authenticated_client_as_user):
        """
        Test that a user cannot retrieve another user's details.
        """
        another_user = User.objects.create_user(username="another_user",
                                                 email="another_user@example.com",
                                                  password="AnotherUserPassword123!")

        response = authenticated_client_as_user.get(f"/users/{another_user.id}")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_retrieve_user_details_as_admin(self, authenticated_client_as_admin, create_normal_user):
        """
        Test that an admin user can retrieve any user's details.
        """
        response = authenticated_client_as_admin.get(f"/users/{create_normal_user.id}")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["username"] == create_normal_user.username

    def test_create_user_as_admin_not_allowed(self,  authenticated_client_as_admin):
        """
        Test creating a new user as an admin via '/users' endpoint is NOT ALLOWED
        """
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "NewUserPassword123!",
        }
        response = authenticated_client_as_admin.post("/users", data=data)
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_update_user_not_allowed(self, authenticated_client_as_user, create_normal_user):
        """
        Test updating a user data from user endpoint forbidden
        """
        data = {
            "email": "updateduser@example.com",
        }
        response = authenticated_client_as_user.patch(f"/users/{create_normal_user.id}", data=data)
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


@pytest.mark.django_db
class TestBookViewSet:

    def test_list_books(self, api_client, create_test_books ):
        """
        Test retrieving the list of books.
        """
        response = api_client.get("/books")
        assert response.status_code == 200
        assert len(response.data['results']) == len(create_test_books)


    def test_retrieve_book(self, api_client, create_test_books):
        """
        Test retrieving a specific book by ID.
        """
        book = create_test_books[0]
        response = api_client.get(f"/books/{book.id}")
        assert response.status_code == 200
        assert response.data["title"] == book.title
        assert response.data["description"] == book.description


    def test_create_book(self, authenticated_client_as_admin, create_test_author):
        """
        Test creating a new book.
        """
        data = {
            "title": "New Book",
            "description": "New book description",
            "authors": [create_test_author.id],
        }
        response = authenticated_client_as_admin.post("/books", data=data)
        assert response.status_code == 201
        assert response.data["title"] == "New Book"

    def test_create_book_unauthenticated(self, api_client, create_test_author):
        """
        Test creating a book without authentication.
        """
        data = {
            "title": "Unauthorized Book",
            "description": "This book should not be created",
            "authors": [create_test_author.id],
        }
        response = api_client.post("/books", data=data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_book(self, authenticated_client_as_admin, create_test_books):
        """
        Test updating an existing book as an authenticated admin user.
        """
        book = create_test_books[0]
        data = {
            "title": "Updated Book Title",
        }
        response = authenticated_client_as_admin.patch(f"/books/{book.id}", data=data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == "Updated Book Title"

    def test_delete_book(self, authenticated_client_as_admin, create_test_books):
        """
        Test deleting a book as an authenticated admin user.
        """
        book = create_test_books[0]
        response = authenticated_client_as_admin.delete(f"/books/{book.id}")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Book.objects.filter(id=book.id).exists()

    def test_search_books_by_title(self, api_client, create_test_books):
        """
        Test searching books by title.
        """
        response = api_client.get("/books?search=Book 1")
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert len(response.data['results']) == 1
        results_list = response.data['results']
        assert results_list[0].get("description") == "Description 1"
        assert results_list[0].get("title") == "Book 1"

    def test_search_books_by_author_name(self, api_client, create_test_books, create_test_author):
        """
        Test searching books by author name.
        """
        response = api_client.get(f"/books?search={create_test_author.name}")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) > 0
        assert create_test_author.name in response.data['results'][0]["authors"][0]["name"]


@pytest.mark.django_db
class TestAuthorViewSet:

    @pytest.fixture
    def create_author(self):
        def make_author(name="John Doe"):
            return Author.objects.create(name=name)
        return make_author

    def test_list_authors(self, api_client):
        """
        Test the list endpoint for Authors
        """
        url = reverse('author-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_retrieve_single_author(self, api_client, create_author):
        author = create_author()
        url = reverse('author-detail', args=[author.id])
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_create_author_unauthenticated(self, api_client):
        url = reverse('author-list')
        payload = {"name": "New Author"}
        response = api_client.post(url, payload)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_author_authenticated(self, authenticated_client_as_user):
        url = reverse('author-list')
        payload = {"name": "New Author"}
        response = authenticated_client_as_user.post(url, payload)
        assert response.status_code == status.HTTP_201_CREATED
        assert Author.objects.filter(name="New Author").exists()

    def test_update_author_unauthenticated(self, api_client, create_author):
        author = create_author()
        url = reverse('author-detail', args=[author.id])
        payload = {"name": "Updated Name"}
        response = api_client.patch(url, payload)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_author_authenticated(self, authenticated_client_as_user, create_author):
        author = create_author()
        url = reverse('author-detail', args=[author.id])
        payload = {"name": "Updated Name"}
        response = authenticated_client_as_user.patch(url, payload)
        assert response.status_code == status.HTTP_200_OK
        author.refresh_from_db()
        assert author.name == "Updated Name"

    def test_delete_author_unauthenticated(self, api_client, create_author):
        author = create_author()
        url = reverse('author-detail', args=[author.id])
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_delete_author_authenticated(self, authenticated_client_as_user, create_author):
        author = create_author()
        url = reverse('author-detail', args=[author.id])
        response = authenticated_client_as_user.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Author.objects.filter(id=author.id).exists()


@pytest.mark.django_db
class TestFavoriteViewSet:

    def test_get_favorites_unauthenticated(self, api_client):
        """Test that unauthenticated users cannot fetch favorites."""
        response = api_client.get("/favorites")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_favorites_authenticated(self, authenticated_client_as_user, create_normal_user, create_test_books):
        """Test that authenticated users can fetch their favorites."""
        book = create_test_books[0]
        Favorite.objects.create(user=create_normal_user, book=book)

        response = authenticated_client_as_user.get("/favorites")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["title"] == book.title