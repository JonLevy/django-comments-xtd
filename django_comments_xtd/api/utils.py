from django.apps import apps
from rest_framework.generics import get_object_or_404

def get_discussion_from_kwargs(kwargs, return_id):
    Discussion = apps.get_model('comments', 'Discussion')

    if set(kwargs.keys()) == {'item_pk', 'playlist_pk'}:
        disc = get_object_or_404(  # expect to throw this often
            Discussion,
            item__id=kwargs['item_pk'],
            playlist__id=kwargs['playlist_pk']
        )
        return return_id and str(disc.id) or disc
    elif set(kwargs.keys()) == {'content_type', 'object_pk'}:
        if return_id:
            return kwargs['object_pk']
        return get_object_or_404(Discussion, id=kwargs['object_pk'])
    else:
        raise Exception('Unexpected arguments received.')

