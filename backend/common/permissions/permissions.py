from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to access or edit it.
    Assumes the model instance has a `user` attribute.
    """

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_staff:
            return True
        user_field = getattr(obj, 'user', None)
        if user_field:
            return user_field == request.user
        trip_request = getattr(obj, 'trip_request', None)
        if trip_request:
            return getattr(trip_request, 'user', None) == request.user
        return False
