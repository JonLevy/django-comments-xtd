import six

from django.db.models import Prefetch
from django.contrib.contenttypes.models import ContentType

from django_comments.models import CommentFlag
from django_comments.views.moderation import perform_flag, perform_delete
from rest_framework import generics, mixins, status
from rest_framework.response import Response
from rest_framework.views import APIView

from django_comments_xtd import views
from django_comments_xtd.api import serializers
from django_comments_xtd.models import XtdComment, LIKEDIT_FLAG, DISLIKEDIT_FLAG
from django_comments_xtd.utils import get_current_site_id
from rest_framework.exceptions import PermissionDenied, ValidationError

from rest_framework.permissions import IsAuthenticated

# ROIL fork imports
from django_comments_xtd.api.permissions import can_user_access_discussion, \
    can_moderate_comments
from django_comments_xtd.api.utils import get_discussion_from_kwargs
from django_comments.models import Comment
from rest_framework.generics import get_object_or_404
import datetime

class CommentCreate(generics.CreateAPIView):
    """Create a comment."""
    serializer_class = serializers.WriteCommentSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            response = super(CommentCreate, self).post(request, *args, **kwargs)
        else:
            return Response([k for k in six.iterkeys(serializer.errors)],
                            status=400)
        response.data['id'] = self.resp_dict['comment']['id']
        if self.resp_dict['code'] == 201:  # The comment has been created.
            return response
        elif self.resp_dict['code'] in [202, 204, 403]:
            return Response({}, status=self.resp_dict['code'])

    def perform_create(self, serializer):
        self.resp_dict = serializer.save()


class CommentList(generics.ListAPIView):
    """List all comments for a given ContentType and object ID."""
    serializer_class = serializers.ReadCommentSerializer

    def get_queryset(self, **kwargs):
        disc = get_discussion_from_kwargs(self.kwargs, False)

        if not can_user_access_discussion(self.request.user, disc):
            # Need here, instead of permission attribute because object
            # permissions are not tested on list
            raise PermissionDenied
        self.kwargs['object_pk'] = disc.id
        self.kwargs['content_type'] = 'comments-discussion'
        return self.nonfork_get_queryset(**kwargs)

    def nonfork_get_queryset(self, **kwargs):  # func from unforked version
        content_type_arg = self.kwargs.get('content_type', None)
        object_pk_arg = self.kwargs.get('object_pk', None)
        app_label, model = content_type_arg.split("-")
        try:
            content_type = ContentType.objects.get_by_natural_key(app_label,
                                                                  model)
        except ContentType.DoesNotExist:
            qs = XtdComment.objects.none()
        else:
            flags_qs = CommentFlag.objects.filter(flag__in=[
                CommentFlag.SUGGEST_REMOVAL, LIKEDIT_FLAG, DISLIKEDIT_FLAG
            ]).prefetch_related('user')
            prefetch = Prefetch('flags', queryset=flags_qs)
            qs = XtdComment\
                .objects\
                .prefetch_related(prefetch)\
                .filter(
                    content_type=content_type,
                    object_pk=object_pk_arg,
                    site__pk=get_current_site_id(self.request),
                    is_public=True
                )
        return qs


class CommentCount(generics.GenericAPIView):
    """Get number of comments posted to a given ContentType and object ID."""
    serializer_class = serializers.ReadCommentSerializer

    def get_queryset(self):
        content_type_arg = self.kwargs.get('content_type', None)
        object_pk_arg = self.kwargs.get('object_pk', None)
        app_label, model = content_type_arg.split("-")
        content_type = ContentType.objects.get_by_natural_key(app_label, model)
        qs = XtdComment.objects.filter(content_type=content_type,
                                       object_pk=object_pk_arg,
                                       is_public=True)
        return qs

    def get(self, request, *args, **kwargs):
        return Response({'count': self.get_queryset().count()})


class ToggleFeedbackFlag(generics.CreateAPIView, mixins.DestroyModelMixin):
    """Create and delete like/dislike flags."""

    serializer_class = serializers.FlagSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = super(ToggleFeedbackFlag, self).post(request, *args,
                                                        **kwargs)
        if self.created:
            return response
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_create(self, serializer):
        if not self.request.data['flag'] in {'like', 'dislike'}:
            raise Exception("Unexpected flag received.")
        f = getattr(views, 'perform_%s' % self.request.data['flag'])
        self.created = f(self.request, serializer.validated_data['comment'])


class CreateReportFlag(generics.CreateAPIView):
    """Create 'removal suggestion' flags."""

    serializer_class = serializers.FlagSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        return super(CreateReportFlag, self).post(request, *args, **kwargs)

    def perform_create(self, serializer):
        perform_flag(self.request, serializer.validated_data['comment'])


class DeleteComment(APIView):
    """Moderator remove comment"""

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        comment = get_object_or_404(Comment, id=int(request.data['comment']))
        if not can_moderate_comments(request.user, comment):
            raise PermissionDenied
        aa = perform_delete(self.request, comment)
        return Response(status=status.HTTP_201_CREATED)


class EditComment(generics.UpdateAPIView):
    """User edit their own comment."""

    serializer_class = serializers.ReadCommentSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        if set(self.request.data.keys()) != {'comment_id', 'comment_text'}:
            raise PermissionDenied
        comment = get_object_or_404(XtdComment,
            id=int(self.request.data['comment_id']))

        if comment.user != self.request.user:  # TODO move to a permission
            raise PermissionDenied
        if comment.comment == self.request.data['comment_text']:  #no change
            raise ValidationError('Editing requires a change in text.')
        comment.edited = True
        comment.submit_date = datetime.datetime.now()
        comment.comment = self.request.data['comment_text']
        return comment
