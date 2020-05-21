from django.apps import apps
from rest_framework.generics import get_object_or_404
from rest_framework import permissions
from rest_framework.exceptions import MethodNotAllowed, PermissionDenied, \
    NotFound


def can_user_access_dicussion(user, discussion):
    playlist = discussion.playlist
    if playlist.public:
        return
    PlaylistUserContext = apps.get_model('playlists', 'PlaylistUserContext')
    plc = get_object_or_404(
        PlaylistUserContext, user=user, playlist=playlist)
    if PlaylistUserContext.ROLE_ORDINALS[plc.role] < 1:
        raise NotFound


#class CanAccessComments(permissions.BasePermission):
#    "Can participate in the comments."
#    def has_object_permission(self, request, view, obj):
#        return False
#        import pdb; pdb.set_trace()
#        0
