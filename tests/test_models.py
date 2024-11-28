from library.models import Book, Author
import pytest

@pytest.mark.django_db
class TestBookModel:
    def test_create_book(self):
        book = Book.objects.create(
            title="Sample Book",
            language="EN",
            work_id="12345",
            num_pages=200
        )
        assert book.title == "Sample Book"
        assert book.language == "EN"
        assert book.work_id == "12345"
        assert book.num_pages == 200

    def test_create_book_with_authors(self):
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
