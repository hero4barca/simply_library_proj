from django.db import models

# Create your models here.

class Author(models.Model):
    first_name = models.CharField(max_length=20 )
    last_name = models.CharField(max_length=20 )

    def __str__(self) -> str:
        return f'{self.first_name} {self.last_name}'


class Book(models.Model):
    title = models.CharField(max_length=50)
    published_on = models.DateTimeField(auto_now_add=True)
    author = models.ManyToManyField(Author)

    class Meta:
        ordering = ["title"]

    def __str__(self) -> str:
        return f'{self.title}; {self.published_on}'
