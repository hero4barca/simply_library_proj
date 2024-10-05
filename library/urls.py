
from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import TokenRefreshView

from .views import UserViewSet, BookViewSet, AuthorViewSet, RegisterView, LoginView, FavoriteViewSet

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'users', UserViewSet)
router.register(r'book-authors', AuthorViewSet)
router.register(r'books', BookViewSet)
router.register(r'favorite', FavoriteViewSet, basename='favorite')

urlpatterns = [
    path('api/register', RegisterView.as_view(), name='register'),
    path('api/login', LoginView.as_view(), name='login'),
    path('api/token/refresh', TokenRefreshView.as_view(), name='token_refresh'),

    path('', include(router.urls)),
]