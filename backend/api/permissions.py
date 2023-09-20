from rest_framework import permissions
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS or obj.author == request.user


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_staff)


class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        raise MethodNotAllowed("Добавление запрещено!")


class IsAuthorOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated):
            return True

    def has_object_permission(self, request, view, obj):
        if (request.method in SAFE_METHODS
                or obj.author == request.user):
            return True
