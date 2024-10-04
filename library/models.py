from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class Author(models.Model):
    name = models.CharField(max_length=50 )

    def __str__(self) -> str:
        return f'{self.name}'


class Book(models.Model):
    title = models.CharField(max_length=50)
    published_on = models.DateField(null=True)
    authors = models.ManyToManyField(Author)

    class Meta:
        ordering = ["title"]

    def __str__(self) -> str:
        return f'{self.title}; {self.published_on}'


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    book = models.ForeignKey(Book, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'book')  # Ensure each book is only added once to favorites per user

    def __str__(self):
        return f'{self.user.username} - {self.book.title}'
