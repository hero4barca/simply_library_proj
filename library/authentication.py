from rest_framework_simplejwt.authentication import JWTAuthentication

class JWTAuthenticationForWriteActions(JWTAuthentication):
    """
    Custom JWT authentication that only enforces authentication for
    write actions (POST, PUT, PATCH, DELETE), while allowing GET requests
    without authentication.
    """
    def authenticate(self, request):
        # If the request method is safe (e.g., GET), do not enforce authentication
        if request.method in ['GET']:
            return None  # Allow unauthenticated access for GET requests

        # For non-safe methods, use the default JWT authentication
        return super().authenticate(request)