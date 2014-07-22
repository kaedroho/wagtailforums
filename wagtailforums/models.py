from django.db import models
from django.shortcuts import render, redirect
from django.conf import settings

from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.signals import page_published
from wagtail.wagtailcore.url_routing import RouteResult
from wagtail.wagtailadmin.edit_handlers import FieldPanel


class BaseForumPost(Page):
    message = models.TextField()
    posted_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, editable=False)
    posted_at = models.DateTimeField(auto_now_add=True, editable=False)

    is_abstract = True

    class Meta:
        abstract = True

BaseForumPost.content_panels = Page.content_panels + [
    FieldPanel('message', classname="full"),
]


class BaseForumReply(BaseForumPost):
    @classmethod
    def get_form_class(cls):
        from wagtailforums.forms import ForumReplyForm
        return ForumReplyForm

    @property
    def edit_url(self):
        return self.url + 'edit/'

    @property
    def delete_url(self):
        return self.url + 'delete/'

    def route(self, request, path_components):
        if self.live:
            if path_components == ['edit']:
                return RouteResult(self, kwargs=dict(action='edit'))

            if path_components == ['delete']:
                return RouteResult(self, kwargs=dict(action='delete'))

        return super(ForumReply, self).route(request, path_components)

    def edit_view(self, request):
        form = self.get_form_class()(request.POST or None, request.FILES or None, instance=self)

        if form.is_valid():
            form.save()
            self.save_revision(user=request.user)
            page_published.send(sender=self.__class__, instance=self)

            return redirect(self.get_parent().url)
        else:
            context = self.get_context(request)
            context['form'] = form
            return render(request, 'wagtailforums/forum_reply_edit.html', context)

    def delete_view(self, request):
        if request.method == 'POST':
            self.live = False
            self.save()
            return redirect(self.get_parent().url)
        else:
            return render(request, 'wagtailforums/forum_reply_delete.html', self.get_context(request))

    def serve(self, request, action='view'):
        if action == 'edit':
            return self.edit_view(request)

        if action == 'delete':
            return self.delete_view(request)

        return super(BaseForumReply, self).serve(request)

    is_abstract = True

    class Meta:
        abstract = True


class BaseForumTopic(BaseForumPost):
    @classmethod
    def get_form_class(cls):
        from wagtailforums.forms import ForumReplyForm
        return ForumReplyForm

    @property
    def edit_url(self):
        return self.url + 'edit/'

    @property
    def delete_url(self):
        return self.url + 'delete/'

    def route(self, request, path_components):
        if self.live:
            if path_components == ['edit']:
                return RouteResult(self, kwargs=dict(action='edit'))

            if path_components == ['delete']:
                return RouteResult(self, kwargs=dict(action='delete'))

        return super(BaseForumTopic, self).route(request, path_components)

    def main_view(self, request):
        form = ForumReply.get_form_class()(request.POST or None, request.FILES or None)

        if form.is_valid():
            page = form.save(commit=False)
            page.owner = page.posted_by = request.user
            self.add_child(instance=page)
            page.save_revision(user=request.user)
            page_published.send(sender=page.__class__, instance=page)
            return redirect(self.url)
        else:
            context = self.get_context(request)
            context['reply_form'] = form
            return render(request, self.get_template(request), context)

    def edit_view(self, request):
        form = self.get_form_class()(request.POST or None, request.FILES or None, instance=self)

        if form.is_valid():
            form.save()
            self.save_revision(user=request.user)
            page_published.send(sender=self.__class__, instance=self)

            return redirect(self.url)
        else:
            context = self.get_context(request)
            context['form'] = form
            return render(request, 'wagtailforums/forum_topic_edit.html', context)

    def delete_view(self, request):
        if request.method == 'POST':
            self.live = False
            self.save()
            return redirect(self.get_parent().url)
        else:
            return render(request, 'wagtailforums/forum_topic_delete.html', self.get_context(request))

    def serve(self, request, action='view'):
        if action == 'view':
            return self.main_view(request)

        if action == 'edit':
            return self.edit_view(request)

        if action == 'delete':
            return self.delete_view(request)

    is_abstract = True

    class Meta:
        abstract = True


class BaseForumIndex(Page):
    @property
    def search_url(self):
        return self.url + 'search/'

    def route(self, request, path_components):
        if self.live:
            if path_components == ['search']:
                return RouteResult(self, kwargs=dict(action='search'))

        return super(BaseForumIndex, self).route(request, path_components)

    def search_view(self, request):
        if 'q' in request.GET:
            query_string = request.GET['q']
            search_results = Page.objects.live().descendant_of(self).search(query_string)
        else:
            query_string = None
            search_results = Page.objects.none()

        return render(request, 'wagtailforums/forum_index_search.html', {
            'query_string': query_string,
            'search_results': search_results,
        })

    def serve(self, request, action='view'):
        if action == 'search':
            return self.search_view(request)

        return super(BaseForumIndex, self).serve(request)

    is_abstract = True

    class Meta:
        abstract = True
