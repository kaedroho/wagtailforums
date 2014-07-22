from django.test import TestCase

from wagtail.wagtailcore.models import Page

from test.models import ForumIndex, ForumTopic


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

    def test_get_topics(self):
        # Get topics
        topics = self.forum_index.get_topics()

        # Check that topics for this page are included
        self.assertIn(self.forum_topics[0].page_ptr, topics)

        # Check that the unpublished topic was not included
        self.assertNotIn(self.unpublished_topic.page_ptr, topics)

        # Check that no topics from the sub forum were included
        self.assertNotIn(self.sub_forum_topics[0].page_ptr, topics)

    def test_get_all_topics(self):
        # Get topics
        topics = self.forum_index.get_all_topics()

        # Check that topics for this page are included
        self.assertIn(self.forum_topics[0].page_ptr, topics)

        # Check that the unpublished topic was not included
        self.assertNotIn(self.unpublished_topic.page_ptr, topics)

        # Check that topics from the sub forum were included
        self.assertIn(self.sub_forum_topics[0].page_ptr, topics)

    def test_get_main(self):
        response = self.client.get(self.forum_index.url)

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'test/forum_index.html')
