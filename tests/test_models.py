import pytest
from django.contrib.auth.models import User

from library.models import Book, Author, Favorite

@pytest.mark.django_db
class TestBookModel:
    def create_book(self):
        book = Book.objects.create(
            title="Sample Book",
            language="EN",
            work_id="12345",
            num_pages=200
        )
        return book

    def create_book_with_authors(self):
        # Create authors
        author1 = Author.objects.create(name="Author One")
        author2 = Author.objects.create(name="Author Two")

        # Create a book and associate authors
        book = Book.objects.create(
            title="Book with Authors",
            language="EN",
            num_pages=300
        )
        book.authors.add(author1, author2)
        return book, author1, author2


    def test_create_book(self):
        book = self.create_book()
        assert book.title == "Sample Book"
        assert book.language == "EN"
        assert book.work_id == "12345"
        assert book.num_pages == 200

    def test_create_book_with_authors(self):
        book, author1, author2 = self.create_book_with_authors()
        assert book.authors.count() == 2
        assert author1 in book.authors.all()
        assert author2 in book.authors.all()

    def test_get_authors_str(self):
        book, author1, author2 = self.create_book_with_authors()
        authors_str = book.get_authors_str()

        assert authors_str == f"{author1}, {author2}"

    def test_str_representation(self):
        # Test the __str__ method

        book, _, _ = self.create_book_with_authors()
        assert str(book) == "Book with Authors; Author One, Author Two"

    def test_ordering_by_title(self):
        # Create multiple books with different titles
        Book.objects.create(title="C Book", language="EN")
        Book.objects.create(title="A Book", language="EN")
        Book.objects.create(title="B Book", language="EN")

        # Fetch books and check ordering
        books = Book.objects.all()
        titles = [book.title for book in books]
        assert titles == ["A Book", "B Book", "C Book"]

@pytest.mark.django_db
class TestFavoriteModel:
    def test_create_favorite(self):
        # Create a user, author, and book
        user = User.objects.create_user(username="testuser", password="password123")
        author = Author.objects.create(name="Test Author")
        book = Book.objects.create(title="Test Book")
        book.authors.add(author)

        # Create a favorite
        favorite = Favorite.objects.create(user=user, book=book)

        # Assertions
        assert favorite.user == user
        assert favorite.book == book
        assert str(favorite) == "testuser - Test Book"
