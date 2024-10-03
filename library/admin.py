from django.contrib import admin

from .models import Author, Book


# Register your models here.
@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name")

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ["title", "published_on", "get_authors" ]

    def get_authors(self, obj):
        authors_string = ""
        for author in obj.authors.all():
            authors_string += str(author) + "; "
        return authors_string

    get_authors.short_description = "author(s)"
