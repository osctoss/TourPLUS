from typing import Any
from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to access or edit it.
    Assumes the model instance has a `user` attribute.
    """

    def has_object_permission(self, request: Any, view: Any, obj: Any) -> bool:
        if not getattr(request, 'user', None) or not request.user.is_authenticated:
            return False
        if getattr(request.user, 'is_staff', False):
            return True
        user_field = getattr(obj, 'user', None)
        if user_field:
            return bool(user_field == request.user)
        trip_request = getattr(obj, 'trip_request', None)
        if trip_request:
            return bool(getattr(trip_request, 'user', None) == request.user)
        return False

