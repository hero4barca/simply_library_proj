import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from library.models import Author, Book

@pytest.fixture
def create_user(db):
    """
    Fixture to create a test user for login tests.
    """
    return User.objects.create_user(username="testuser", email="testuser@example.com", password="StrongPassword123!")

@pytest.fixture
def api_client():
    """
    Fixture to provide an instance of APIClient for DRF tests.
    """
    return APIClient()

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


@pytest.fixture
def authenticated_client_as_admin(api_client, create_superuser):
    """
    Fixture to return an API client authenticated as an admin user.
    """
    response = api_client.post('/api/login', {
        'username': 'admin',
        'password': 'AdminPassword123!'
    })
    assert response.status_code == 200
    token = response.data['access']
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    return api_client


@pytest.fixture
def authenticated_client_as_user(api_client, create_normal_user):
    """
    Fixture to return an API client authenticated as a regular user.
    """
    response = api_client.post('/api/login', {
        'username': 'testuser',
        'password': 'UserPassword123!'
    })
    assert response.status_code == 200
    token = response.data['access']
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    return api_client

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