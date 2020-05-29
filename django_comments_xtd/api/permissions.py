from django.apps import apps
from rest_framework.exceptions import PermissionDenied

from django_comments_xtd.models import XtdComment


def not_my_comment(request):
    cmt = XtdComment.objects.get(id=int(request.data['comment']))
    if cmt.user == request.user:
        raise PermissionDenied

def can_user_access_discussion(user, discussion):
    playlist = discussion.playlist
    if playlist.public:
        return
    PlaylistUserContext = apps.get_model('playlists', 'PlaylistUserContext')
    try:
        plc = PlaylistUserContext.objects.get(user=user, playlist=playlist)
    except PlaylistUserContext.DoesNotExist:
        raise PermissionDenied
    follower_rank = PlaylistUserContext.ROLE_ORDINALS[
        PlaylistUserContext.FOLLOWER]
    if PlaylistUserContext.ROLE_ORDINALS[plc.role] < follower_rank:
        raise PermissionDenied

def can_moderate_comments(user, comment):
    discussion = comment.content_type.model_class().objects.get(
        id=comment.object_pk)
    PlaylistUserContext = apps.get_model(app_label='playlists',
        model_name='PlaylistUserContext')
    try:
        plc = PlaylistUserContext.objects.get(user=user,
            playlist=discussion.playlist)
    except PlaylistUserContext.DoesNotExist:
        raise PermissionDenied

    admin_rank = PlaylistUserContext.ROLE_ORDINALS[
        PlaylistUserContext.ADMIN]
    if PlaylistUserContext.ROLE_ORDINALS[plc.role] >= admin_rank:
        return
    raise PermissionDenied
