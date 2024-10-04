from django.db import models

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
