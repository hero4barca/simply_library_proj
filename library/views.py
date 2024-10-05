from django.shortcuts import render

from django.contrib.auth.models import User
from rest_framework import viewsets

from rest_framework import status, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication


from .models import Book, Author, Favorite
from .serializers import UserSerializer, BookSerializer, AuthorSerializer, UserRegistrationSerializer
from .permissions import IsAuthenticatedForWriteActions
from .authentication import JWTAuthenticationForWriteActions
from .recommendations import recommend_books

# Create your views here.
# ViewSets define the view behavior.

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({'detail': 'User registered successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    http_method_names = ["get", "post", "put", "patch", "delete"]

    # cuustom authentication and permission
    authentication_classes = [JWTAuthenticationForWriteActions]
    permission_classes = [IsAuthenticatedForWriteActions]

    # add search filter
    filter_backends = [filters.SearchFilter]

    # Specify fields to search: "title" (Book's field) and "authors__name" (related Author model's field)
    search_fields = ['title', 'authors__name']

class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    http_method_names = ["get", "post", "put", "patch", "delete"]
    authentication_classes = [JWTAuthenticationForWriteActions]
    permission_classes = [IsAuthenticatedForWriteActions]

class FavoriteViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    http_method_names = ["get", "post", "delete"]


    def list(self, request):
        # Get all favorite books for the user
        favorites = Favorite.objects.filter(user=request.user)
        serializer = BookSerializer([fav.book for fav in favorites], many=True) # use book serializer
        return Response(serializer.data)

    def create(self, request):
        """
        Handles 'create' action
        Checks that the book does exist before creating relation between user and book

        @Param book_id in request body
        """
        book_id = request.data.get('book_id')
        try:
            book = Book.objects.get(id=book_id)
        except Book.DoesNotExist:
            return Response({'error': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)

        if Favorite.objects.filter(user=request.user).count() >= 20:
            return Response({'error': 'Cannot add more than 20 favorites'}, status=status.HTTP_400_BAD_REQUEST)

        favorite, created = Favorite.objects.get_or_create(user=request.user, book=book)
        if created:
            # Return recommendations when a new favorite is added
            recommendations = recommend_books(request.user)
            return Response({
                'message': 'Book added to favorites',
                'recommendations': recommendations
            })
        return Response({'message': 'Book already in favorites'}, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        """
        Delete view function.

        @param pk: pk of the Book object; NOT Favourite model

        """
        try:
            favorite = Favorite.objects.get(user=request.user, book_id=pk) # query by book_id not object pk
            favorite.delete()
            return Response({'message': 'Book removed from favorites'}, status=status.HTTP_200_OK)
        except Favorite.DoesNotExist:
            return Response({'error': 'Favorite book not found'}, status=status.HTTP_404_NOT_FOUND)
