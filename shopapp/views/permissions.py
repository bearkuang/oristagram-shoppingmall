from rest_framework import permissions

class IsCustomer(permissions.BasePermission):
    def has_permission(self, request, view):
        # JWT 인증을 사용
        return request.auth and request.auth.get('user_type') == 'customer'