from rest_framework import permissions

class IsManagerOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        # Allow GET request to anyone
        # if request.method == 'GET':
        #     return []
        
        # Check if the user is in the 'manager' group
        return request.user and request.user.groups.filter(name='Manager').exists()