import os

from django.db import models
from django.shortcuts import render, redirect
from django.conf import settings
from django.conf.urls import url
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.utils.text import slugify
from django import forms

from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.utils import resolve_model_string
from wagtail.wagtailadmin.edit_handlers import FieldPanel
from wagtail.contrib.wagtailroutablepage.models import RoutablePageMixin


class ForumPageMixin(RoutablePageMixin):
    subpage_urls = (
        url(r'^$', 'main_view', name='main'),
        url(r'^new_post/$', 'new_post_view', name='new_post'),
    )

    post_model = None

    @classmethod
    def get_post_model(cls):
        if not cls.post_model:
            return

        return resolve_model_string(cls.post_model)

    @property
    def new_post_url(self):
        return self.url + self.reverse_subpage('new_post')

    def user_can_create_post(self, user):
        # If theres no post model, no posts can be created
        if not self.get_post_model():
            return False

        # Make sure the user is active
        if not user.is_active:
            return False

        # Check if the user has permission to do this in wagtail
        if self.permissions_for_user(user).can_add_subpage():
            return True

        return True

    def user_can_publish_post(self, user):
        # Users need to be able to create posts before they can publish them
        if not self.user_can_create_post(user):
            return False

        # Check if the user has permission to do this in wagtail
        if self.permissions_for_user(user).can_publish_subpage():
            return True

        return True

    def get_next_post_number(self):
        children = self.get_post_model().objects.child_of(self)

        return (children.aggregate(models.Max('post_number'))['post_number__max'] or 0) + 1

    def get_create_post_redirect_url(self, post):
        return post.url

    def new_post_view(self, request):
        if not self.user_can_create_post(request.user):
            raise PermissionDenied

        form = self.get_post_model().get_form_class()(request.POST or None, request.FILES or None)

        if form.is_valid():
            publishing = self.user_can_publish_post(request.user)

            page = form.save(commit=False)
            page.owner  = request.user
            page.post_number = self.get_next_post_number()
            page.slug = page.get_slug()
            if not page.title:
                page.title = str(page.post_number)
            page.live = False
            page.has_unpublished_changes = True

            self.add_child(instance=page)
            revision = page.save_revision(user=request.user, submitted_for_moderation=not publishing)

            if publishing:
                revision.publish()

            return redirect(self.get_create_post_redirect_url(page))
        else:
            context = self.get_context(request)
            context['post_form'] = form
            context['user_can_publish_post'] = self.user_can_publish_post(request.user)
            return render(request, get_template_name(self.template, 'new_post'), context)

    def main_view(self, request):
        form = self.get_post_model().get_form_class()(request.POST or None, request.FILES or None)

        context = self.get_context(request)
        context['post_form'] = form
        context['user_can_create_post'] = self.user_can_create_post(request.user)
        context['user_can_publish_post'] = self.user_can_publish_post(request.user)
        return render(request, self.get_template(request), context)

    class Meta:
        abstract = True


class AbstractForumPost(ForumPageMixin, Page):
    message = models.TextField()
    post_number = models.PositiveIntegerField(editable=False, null=True)

    subpage_urls = ForumPageMixin.subpage_urls + (
        url(r'^edit/$', 'edit_view', name='edit'),
        url(r'^delete/$', 'delete_view', name='delete'),
    )

    form_fields = ('message', )

    @classmethod
    def get_form_class(cls):
        class form(forms.ModelForm):
            class Meta:
                model = cls
                fields = cls.form_fields

        form.__name__ = cls.__name__ + 'Form'

        return form

    @property
    def edit_url(self):
        return self.url + self.reverse_subpage('edit')

    @property
    def delete_url(self):
        return self.url + self.reverse_subpage('delete')

    def user_can_edit(self, user):
        # Check if the user has permission to do this in wagtail
        if self.permissions_for_user(user).can_edit():
            return True

        # Make sure the user is active
        if not user.is_active:
            return False

        # Owner can edit
        if user == self.owner:
            return True

        return False

    def user_can_delete(self, user):
        # Check if the user has permission to do this in wagtail
        if self.permissions_for_user(user).can_delete():
            return True

        # Make sure the user is active
        if not user.is_active:
            return False

        # Owner can delete
        if user == self.owner:
            return True

        return False

    def get_earliest_revision(self):
        return self.revisions.order_by('-created_at').last()

    # get_latest_revision is implemented in wagtailcore.Page

    def get_posted_at(self):
        return self.get_earliest_revision().created_at

    def get_posted_by(self):
        return self.get_earliest_revision().user

    def get_edited_at(self):
        return self.get_latest_revision().created_at

    def get_edited_by(self):
        return self.get_latest_revision().user

    def get_slug(self):
        if self.title:
            return str(self.post_number) + '-' + slugify(self.title)
        else:
            return str(self.post_number)

    def get_context(self, request):
        context = super(AbstractForumPost, self).get_context(request)
        context['user_can_edit'] = self.user_can_edit(request.user)
        context['user_can_delete'] = self.user_can_delete(request.user)
        return context

    def get_edit_redirect_url(self):
        return self.url

    def edit_view(self, request):
        if not self.user_can_edit(request.user):
            if request.method == 'POST':
                raise PermissionDenied
            else:
                return redirect(self.url)

        form = self.get_form_class()(request.POST or None, request.FILES or None, instance=self)

        if form.is_valid():
            form.save(commit=False)
            self.save_revision(user=request.user).publish()

            return redirect(self.get_edit_redirect_url())
        else:
            context = self.get_context(request)
            context['form'] = form
            return render(request, get_template_name(self.template, 'edit'), context)

    def get_delete_redirect_url(self):
        return self.get_parent().url

    def delete_view(self, request):
        if not self.user_can_delete(request.user):
            if request.method == 'POST':
                raise PermissionDenied
            else:
                return redirect(self.url)

        if request.method == 'POST':
            self.delete()
            return redirect(self.get_delete_redirect_url())
        else:
            return render(request, get_template_name(self.template, 'delete'), self.get_context(request))

    is_abstract = True

    class Meta:
        abstract = True

AbstractForumPost.content_panels = Page.content_panels + [
    FieldPanel('message', classname="full"),
]


class AbstractForumReply(AbstractForumPost):
    def get_edit_redirect_url(self):
        return self.get_parent().url

    is_abstract = True

    class Meta:
        abstract = True


class AbstractForumTopic(AbstractForumPost):
    form_fields = ('title', 'message')

    def get_create_post_redirect_url(self, post):
        return self.url

    is_abstract = True

    class Meta:
        abstract = True


class AbstractForumIndex(ForumPageMixin, Page):
    subpage_urls = ForumPageMixin.subpage_urls + (
        url(r'^search/$', 'search_view', name='search'),
    )

    @property
    def search_url(self):
        return self.url + self.reverse_subpage('search')

    def search_view(self, request):
        if 'q' in request.GET:
            query_string = request.GET['q']
            search_results = self.get_post_model().objects.live().descendant_of(self).search(query_string)
        else:
            query_string = None
            search_results = self.get_post_model().objects.none()

        return render(request, get_template_name(self.template, 'search'), {
            'query_string': query_string,
            'search_results': search_results,
        })

    is_abstract = True

    class Meta:
        abstract = True


def get_template_name(main_template_name, view_name):
    root, ext = os.path.splitext(main_template_name)
    return root + '_' + view_name + ext
