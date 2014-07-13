from django import forms

from wagtailforums.models import ForumIndex, ForumTopic, ForumReply


class ForumReplyForm(forms.ModelForm):

    class Meta:
        model = ForumReply
        fields = ('message', )
