from rest_framework.permissions import SAFE_METHODS
from rest_framework.permissions import BasePermission
from rest_framework.permissions import IsAuthenticatedOrReadOnly


class IsStaffOrReadOnly(IsAuthenticatedOrReadOnly):
    def has_object_permission(self, request, view, obj):
        return (
            request.method in ('GET',)
            or (request.user == obj.author)
            or request.user.is_staff
        )


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return (
            request.method in ('GET',)
            or request.user.is_authenticated
            and request.user.is_staff
        )


class AuthorOrReadOnly(IsAuthenticatedOrReadOnly):
    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or obj.author == request.user
        )


class IsAuthor(IsAuthenticatedOrReadOnly):
    def has_object_permission(self, request, view, obj):
        return (request.user == obj)
