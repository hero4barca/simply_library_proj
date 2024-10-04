from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class Author(models.Model):
    name = models.CharField(max_length=50 )

    def __str__(self) -> str:
        return f'{self.name}'


class Book(models.Model):
    title = models.CharField(max_length=50)
    authors = models.ManyToManyField(Author)
    language = models.CharField(max_length=10, blank=True)
    work_id = models.CharField(max_length=20, blank=True)
    edition_information = models.CharField(max_length=50, blank=True)
    publisher = models.CharField(max_length=50, blank=True)
    num_pages = models.IntegerField(null=True)
    series_id = models.CharField(max_length=20, blank=True)
    series_name = models.CharField(max_length=50, blank=True)
    series_position = models.CharField(max_length=10, blank=True)
    description = models.TextField( blank=True)

    class Meta:
        ordering = ["title"]

    def __str__(self) -> str:
        return f'{self.title}; {self.get_authors_str()}'

    def get_authors_str(self):
        authors_str = ""
        for author in self.authors.all():
            authors_str += author.name
        return authors_str


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    book = models.ForeignKey(Book, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'book')  # Ensure each book is only added once to favorites per user

    def __str__(self):
        return f'{self.user.username} - {self.book.title}'
