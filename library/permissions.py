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

class IsAdminOrSelf(BasePermission):
    """
    Custom permission to allow:
    - Admins to access the list view (GET /users).
    - Users to access their own details (GET /users/{id}).
    """

    def has_permission(self, request, view):
        # Allow only admin users to access the list endpoint
        if view.action == "list":
            return request.user.is_staff

        # Allow all authenticated users for other actions (detail view)
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Allow access only if the user is requesting their own data or if they are an admin
        return request.user.is_staff or obj == request.user