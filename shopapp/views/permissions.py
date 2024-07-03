from rest_framework import permissions
from rest_framework.permissions import BasePermission

class IsAuthenticatedCompany(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_company)

class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        print(f"Checking IsCustomer permission for user: {request.user}")
        print(f"Is authenticated: {request.user.is_authenticated}")
        print(f"Is company: {getattr(request.user, 'is_company', None)}")
        print(f"Is customer: {getattr(request.user, 'is_customer', None)}")
        return bool(request.user and request.user.is_authenticated and not request.user.is_company)