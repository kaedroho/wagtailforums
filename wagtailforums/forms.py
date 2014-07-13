from django import forms

from wagtailforums.models import ForumIndex, ForumTopic, ForumReply


class ForumTopicForm(forms.ModelForm):

    class Meta:
        model = ForumTopic
        fields = ('message', )


class ForumReplyForm(forms.ModelForm):

    class Meta:
        model = ForumReply
        fields = ('message', )
