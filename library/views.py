from django.shortcuts import render

from django.contrib.auth.models import User
from rest_framework import viewsets

from rest_framework import status, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
# from rest_framework_simplejwt.authentication import JWTAuthentication


from .models import Book, Author
from .serializers import UserSerializer, BookSerializer, AuthorSerializer, UserRegistrationSerializer
from .permissions import IsAuthenticatedForWriteActions
from .authentication import JWTAuthenticationForWriteActions

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
