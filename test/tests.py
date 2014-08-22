from django.test import TestCase
from django.contrib.auth.models import User

from wagtail.wagtailcore.models import Page
from wagtail.tests.utils import WagtailTestUtils

from test.models import ForumIndex, ForumTopic, ForumReply


class TestForumIndex(TestCase):
    def setUp(self):
        self.home_page = Page.objects.get(id=2)

        # Create a forum index
        self.forum_index = self.home_page.add_child(instance=ForumIndex(
            title="Forums",
            slug='forums',
            live=True,
        ))

        # Create some topics
        self.forum_topics = [
            self.forum_index.add_child(instance=ForumTopic(
                title="Topic " + str(i),
                slug='topic-' + str(i),
                live=True,
            ))
            for i in range(10)
        ]

        # Create an unpublished topic
        self.unpublished_topic = self.forum_index.add_child(instance=ForumTopic(
            title="Unpublished topic",
            slug='unpublished-topic',
            live=False,
        ))

        # Create a subforum
        self.sub_forum_index = self.forum_index.add_child(instance=ForumIndex(
            title="Subforum",
            slug='subforum',
            live=True,
        ))

        # Create some subforum topics
        self.sub_forum_topics = [
            self.sub_forum_index.add_child(instance=ForumTopic(
                title="Topic " + str(i),
                slug='topic-' + str(i),
                live=True,
            ))
            for i in range(10)
        ]

    def test_get_main(self):
        response = self.client.get(self.forum_index.url)

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'test/forum_index.html')

    def test_get_search(self):
        response = self.client.get(self.forum_index.search_url)

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'test/forum_index_search.html')


class TestForumTopic(TestCase, WagtailTestUtils):
    def setUp(self):
        self.home_page = Page.objects.get(id=2)

        # Create a couple of test users
        self.topic_owner = User.objects.create_user(username='topic_owner', password='hello123')
        self.other_user = User.objects.create_user(username='other_user', password='hello123')

        # Create a forum index
        self.forum_index = self.home_page.add_child(instance=ForumIndex(
            title="Forums",
            slug='forums',
            live=True,
        ))

        # Create a topic
        self.forum_topic = self.forum_index.add_child(instance=ForumTopic(
            title="Topic",
            slug='topic',
            live=True,
            owner=self.topic_owner,
        ))

        # Create some replies
        self.forum_replies = [
            self.forum_topic.add_child(instance=ForumReply(
                title="Reply " + str(i),
                slug='reply-' + str(i),
                live=True,
            ))
            for i in range(10)
        ]

        # Create an unpublished reply
        self.unpublished_reply = self.forum_topic.add_child(instance=ForumReply(
            title="Unpublished reply",
            slug='unpublished-reply',
            live=False,
        ))

    def test_get_main(self):
        response = self.client.get(self.forum_topic.url)

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'test/forum_topic.html')

    def _test_get_edit_good(self):
        response = self.client.get(self.forum_topic.edit_url)

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'test/forum_topic_edit.html')

        # Check form
        self.assertIn('form', response.context)
        self.assertEqual(len(response.context['form'].fields), 3)
        self.assertIn('title', response.context['form'].fields)
        self.assertIn('message', response.context['form'].fields)
        self.assertIn('custom_field', response.context['form'].fields)

    def _test_get_edit_bad(self):
        response = self.client.get(self.forum_topic.edit_url)

        # Response should redirect back to the topic
        self.assertRedirects(response, self.forum_topic.url)

    def test_get_edit_as_admin(self):
        # Login as an admin
        self.user = self.login()

        # Run tests for good result
        self._test_get_edit_good()

    def test_get_edit_as_owner(self):
        # Login as the topic owner
        self.user = self.topic_owner
        self.client.login(username='topic_owner', password='hello123')

        # Run tests for good result
        self._test_get_edit_good()

    def test_get_edit_not_logged_in(self):
        # Run tests for bad result
        self._test_get_edit_bad()

    def test_get_edit_as_other_user(self):
        # Login as the other user
        self.user = self.other_user
        self.client.login(username='other_user', password='hello123')

        # Run tests for bad result
        self._test_get_edit_bad()

    def _test_post_edit_good(self):
        revision_count = self.forum_topic.revisions.count()

        response = self.client.post(self.forum_topic.edit_url, {
            'title': "Topic",
            'message': "Hello",
            'custom_field': "World",
        })

        # Response should redirect back to the topic
        self.assertRedirects(response, self.forum_topic.url)

        # Check that the topic changed
        topic = ForumTopic.objects.get(id=self.forum_topic.id)
        self.assertEqual(topic.message, "Hello")
        self.assertEqual(topic.custom_field, "World")

        # Check revision
        self.assertEqual(topic.revisions.count(), revision_count + 1)
        self.assertEqual(topic.get_latest_revision().user, self.user)

    def _test_post_edit_bad(self):
        response = self.client.post(self.forum_topic.edit_url, {
            'title': "Topic",
            'message': "Hello",
            'custom_field': "World",
        })

        # Check that the user was forbidden
        self.assertEqual(response.status_code, 403)

        # Check that the topic didn't change
        topic = ForumTopic.objects.get(id=self.forum_topic.id)
        self.assertNotEqual(topic.message, "Hello")
        self.assertNotEqual(topic.custom_field, "World")

    def test_post_edit_as_admin(self):
        # Login as an admin
        self.user = self.login()

        # Run tests for good result
        self._test_post_edit_good()

    def test_post_edit_as_owner(self):
        # Login as the topic owner
        self.user = self.topic_owner
        self.client.login(username='topic_owner', password='hello123')

        # Run tests for good result
        self._test_post_edit_good()

    def test_post_edit_not_logged_in(self):
        # Run tests for bad result
        self._test_post_edit_bad()

    def test_post_edit_as_other_user(self):
        # Login as the other user
        self.user = self.other_user
        self.client.login(username='other_user', password='hello123')

        # Run tests for bad result
        self._test_post_edit_bad()

    def _test_get_delete_good(self):
        response = self.client.get(self.forum_topic.delete_url)

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'test/forum_topic_delete.html')

    def _test_get_delete_bad(self):
        response = self.client.get(self.forum_topic.delete_url)

        # Response should redirect back to the topic
        self.assertRedirects(response, self.forum_topic.url)

    def test_get_delete_as_admin(self):
        # Login as an admin
        self.user = self.login()

        # Run tests for good result
        self._test_get_delete_good()

    def test_get_delete_as_owner(self):
        # Login as the topic owner
        self.user = self.topic_owner
        self.client.login(username='topic_owner', password='hello123')

        # Run tests for good result
        self._test_get_delete_good()

    def test_get_delete_not_logged_in(self):
        # Run tests for bad result
        self._test_get_delete_bad()

    def test_get_delete_as_other_user(self):
        # Login as the other user
        self.user = self.other_user
        self.client.login(username='other_user', password='hello123')

        # Run tests for bad result
        self._test_get_delete_bad()

    def _test_post_delete_good(self):
        response = self.client.post(self.forum_topic.delete_url)

        # Response should redirect back to the forum index
        self.assertRedirects(response, self.forum_index.url)

        # Check that the topic was deleted
        self.assertFalse(ForumTopic.objects.filter(id=self.forum_topic.id).exists())

    def _test_post_delete_bad(self):
        response = self.client.post(self.forum_topic.delete_url)

        # Check that the user was forbidden
        self.assertEqual(response.status_code, 403)

        # Check that the topic didn't change
        topic = ForumTopic.objects.get(id=self.forum_topic.id)
        self.assertTrue(topic.live)

    def test_post_delete_as_admin(self):
        # Login as an admin
        self.user = self.login()

        # Run tests for good result
        self._test_post_delete_good()

    def test_post_delete_as_owner(self):
        # Login as the topic owner
        self.user = self.topic_owner
        self.client.login(username='topic_owner', password='hello123')

        # Run tests for good result
        self._test_post_delete_good()

    def test_post_delete_not_logged_in(self):
        # Run tests for bad result
        self._test_post_delete_bad()

    def test_post_delete_as_other_user(self):
        # Login as the other user
        self.user = self.other_user
        self.client.login(username='other_user', password='hello123')

        # Run tests for bad result
        self._test_post_delete_bad()
