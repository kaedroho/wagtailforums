from django.db import models

from wagtail.wagtailcore.models import Page
from wagtail.wagtailadmin.edit_handlers import FieldPanel


class ForumReply(Page):
    message = models.TextField()

    subpage_types = (
        'wagtailforums.ForumReply',
    )

    def get_replies(self):
        return ForumReply.objects.child_of(self)

ForumReply.content_panels = [
    FieldPanel('title', classname="full title"),
    FieldPanel('message', classname="full"),
]


class ForumTopic(Page):
    message = models.TextField()

    # Default class to use for replies to this topic
    # Must be subclass of ``ForumReply``
    default_reply_class = ForumReply

    subpage_types = (
        'wagtailforums.ForumReply',
    )

    def get_replies(self):
        return self.default_reply_class.objects.child_of(self)

ForumTopic.content_panels = [
    FieldPanel('title', classname="full title"),
    FieldPanel('message', classname="full"),
]


class ForumIndex(Page):
    # Default class to use for topics in this forum index
    # Must be subclass of ``ForumTopic``
    default_topic_class = ForumTopic

    def get_forums(self):
        return ForumIndex.objects.child_of(self).live().public()

    def get_topics(self):
        return self.default_topic_class.objects.child_of(self)
