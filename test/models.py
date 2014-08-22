from django.db import models

from wagtailforums.models import BaseForumIndex, BaseForumTopic, BaseForumReply


class ForumReply(BaseForumReply):
    pass


class ForumTopic(BaseForumTopic):
    custom_field = models.TextField()

    reply_model = ForumReply
    form_fields = BaseForumTopic.form_fields + (
        'custom_field',
    )


class ForumIndex(BaseForumIndex):
    topic_model = ForumTopic
