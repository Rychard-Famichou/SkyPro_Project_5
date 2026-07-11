from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):
    """Разрешает все CRUD действия для владельцев"""

    def has_object_permission(self, request, view, obj):
        return getattr(obj, "owner", None) == request.user
