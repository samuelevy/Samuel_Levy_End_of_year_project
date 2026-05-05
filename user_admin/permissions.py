from rest_framework.permissions import BasePermission

class IsAdminUser(BasePermission):
    #only allow access to admin users
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'ADMIN'
    class modifyUser:
        def has_object_permission(self, request, view, obj):
            # obj is the User being modified
            if obj.role == 'ADMIN' and obj != request.user:
                return False  # Can't modify other admins
            return True
    