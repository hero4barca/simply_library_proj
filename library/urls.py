
from django.urls import path, include
from rest_framework import routers

from .views import UserViewSet, BookViewSet, AuthorViewSet

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'users', UserViewSet)
router.register(r'book_authors', AuthorViewSet)
router.register(r'books', BookViewSet)

urlpatterns = [
    path('', include(router.urls)),
]