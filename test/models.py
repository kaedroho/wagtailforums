from django.db import models

from wagtailforums.models import BaseForumIndex, BaseForumPost



class ForumReply(BaseForumPost):
    def edit_redirect_url(self):
        return self.get_parent().url


class ForumTopic(BaseForumPost):
    custom_field = models.TextField()

    reply_model = ForumReply
    form_fields = (
        'title',
        'message',
        'custom_field',
    )

    def get_replies(self):
        return self.get_posts().type(ForumReply)


class ForumIndex(BaseForumIndex):
    topic_model = ForumTopic

    def get_topics(self):
        return self.get_posts().type(ForumTopic)

    def get_all_topics(self):
        return self.get_all_posts().type(ForumTopic)
