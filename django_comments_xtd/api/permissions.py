from django.apps import apps


def can_user_access_discussion(user, discussion):
    playlist = discussion.playlist
    if playlist.public:
        return True
    PlaylistUserContext = apps.get_model('playlists', 'PlaylistUserContext')
    try:
        plc = PlaylistUserContext.objects.get(user=user, playlist=playlist)
    except PlaylistUserContext.DoesNotExist:
        return False
    follower_rank = PlaylistUserContext.ROLE_ORDINALS[
        PlaylistUserContext.FOLLOWER]
    if PlaylistUserContext.ROLE_ORDINALS[plc.role] < follower_rank:
        return False
    return True

def can_moderate_comments(user, comment):
    discussion = comment.content_type.model_class().objects.get(
        id=comment.object_pk)
    PlaylistUserContext = apps.get_model(app_label='playlists',
        model_name='PlaylistUserContext')
    try:
        plc = PlaylistUserContext.objects.get(user=user,
            playlist=discussion.playlist)
    except PlaylistUserContext.DoesNotExist:
        return False

    admin_rank = PlaylistUserContext.ROLE_ORDINALS[
        PlaylistUserContext.ADMIN]
    if PlaylistUserContext.ROLE_ORDINALS[plc.role] >= admin_rank:
        return True
    return False
