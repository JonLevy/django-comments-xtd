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

def can_moderate_comments(user, discussion):
    PlaylistUserContext = apps.get_model(app_label='playlists',
        model_name='PlaylistUserContext')
    try:
        plc = PlaylistUserContext.objects.get(user=user,
            playlist=obj.playlist)
    except PlaylistUserContext.DoesNotExist:
        return False

    admin_rank = PlaylistUserContext.ROLE_ORDINALS[
        PlaylistUserContext.ADMIN]
    if PlaylistUserContext.ROLE_ORDINALS[obj.role] >= admin_rank:
        return True
    return False
