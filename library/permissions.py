from rest_framework.permissions import BasePermission

class IsAuthenticatedForWriteActions(BasePermission):
    """
    Custom permission to allow authenticated users for create, update, and delete actions only.
    Unauthenticated users can still perform read-only actions (GET).
    """
    def has_permission(self, request, view):
        # Allow safe (read-only) methods like GET for everyone
        if request.method in ['GET']:
            return True

        # Require authentication for write methods (POST, PUT, PATCH, DELETE)
        return request.user and request.user.is_authenticated