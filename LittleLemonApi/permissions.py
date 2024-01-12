from rest_framework import permissions

class IsManagerOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.groups.filter(name='Manager').exists()