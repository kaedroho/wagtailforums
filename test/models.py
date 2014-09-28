from django.db import models

from wagtailforums.models import AbstractForumIndex, AbstractForumTopic, AbstractForumReply


class ForumReply(AbstractForumReply):
    pass


class ForumTopic(AbstractForumTopic):
    custom_field = models.TextField()

    post_model = ForumReply
    form_fields = AbstractForumTopic.form_fields + (
        'custom_field',
    )


class ForumIndex(AbstractForumIndex):
    post_model = ForumTopic
