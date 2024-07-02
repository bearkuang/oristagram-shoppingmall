from rest_framework import permissions
from rest_framework.permissions import BasePermission

class IsAuthenticatedCompany(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_company)

class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and hasattr(request.user, 'is_customer') and request.user.is_customer)