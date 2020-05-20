from django.apps import apps
from rest_framework import permissions
from rest_framework.exceptions import MethodNotAllowed, PermissionDenied


class CanAccessComments(permissions.BasePermission):
    "Can particpate in the comments."

    def has_permission(self, request, view):
        return True
        import pdb; pdb.set_trace()
        0
