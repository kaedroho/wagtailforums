from django.db import models
from django.utils.translation import ugettext_lazy as _

from wagtail.wagtailcore.models import Page
from wagtail.wagtailadmin.edit_handlers import FieldPanel


class ForumReply(Page):
    message = models.TextField(_("Message"))

    subpage_types = (
        'wagtailforums.ForumReply',
    )

    def get_replies(self):
        return ForumReply.objects.child_of(self)

ForumReply.content_panels = Page.content_panels + [
    FieldPanel('message', classname="full"),
]


class ForumTopic(Page):
    in_forum_index = models.BooleanField(_("Show in forum index"), default=True)
    message = models.TextField(_("Message"))

    subpage_types = (
        'wagtailforums.ForumReply',
    )

    def get_replies(self):
        return ForumReply.objects.child_of(self)

ForumTopic.content_panels = Page.content_panels + [
    FieldPanel('message', classname="full"),
]

ForumTopic.promote_panels = Page.promote_panels + [
    FieldPanel('in_forum_index'),
]


class ForumIndex(Page):
    in_forum_index = models.BooleanField(_("Show in forum index"), default=True)

    def get_forums(self):
        return ForumIndex.objects.child_of(self).live().public()

    def get_topics(self):
        return ForumTopic.objects.child_of(self)

ForumIndex.promote_panels = Page.promote_panels + [
    FieldPanel('in_forum_index'),
]
