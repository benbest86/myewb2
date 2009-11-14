from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from base_groups.models import BaseGroup
from group_topics.models import GroupTopic

class CreateTopics(TestCase):
    """
    Regression tests for
    https://cotonou.ewb.ca/fastrac/myewb2/ticket/389.
    """

    def setUp(self):
        top_user = User.objects.create_user('super', 'super@ewb.ca')
        self.base_group = BaseGroup.objects.create(slug='bg', creator=top_user)

    def tearDown(self):
        BaseGroup.objects.all().delete()
        User.objects.all().delete()

    def test_create_group_topic(self):
        user = User.objects.get()
        gt = GroupTopic.objects.create(title="test", body="some test text.", group=self.base_group, creator=user)
        # make sure we create a topic
        self.assertTrue(gt)



class DeleteTopics(TestCase):
    """
    Regression tests for
    https://cotonou.ewb.ca/fastrac/myewb2/ticket/388.
    """

    def setUp(self):
        top_user = User.objects.create_user('super', 'super@ewb.ca')
        self.base_group = BaseGroup.objects.create(slug='bg', creator=top_user)

    def tearDown(self):
        BaseGroup.objects.all().delete()
        User.objects.all().delete()

    def test_topic_owner_can_delete(self):
        """
        The owner of a post should be able to delete it.
        """
        post_owner = User.objects.create_user('owner', 'owner@ewb.ca', 'password')
        gt = GroupTopic.objects.create(creator=post_owner, group=self.base_group, title='test', body='words')
        topic_id = gt.id
        self.client.login('owner', 'password')
        response = self.client.post(reverse('topic_delete', kwargs={'topic_id': topic_id}))

        # make sure we get a redirect
        self.assertEquals(response.status_code, 302)
        # make sure the topic is deleted
        self.assertRaises(GroupTopic.DoesNotExist, GroupTopic.objects.get(topic_id))


    def test_other_user_cannot_delete(self):
        """
        A non-owner should not be able to delete a post.
        """
        post_owner = User.objects.create_user('owner', 'owner@ewb.ca', 'password')
        gt = GroupTopic.objects.create(creator=post_owner, group=self.base_group, title='test', body='words')
        topic_id = gt.id
        other_user = User.objects.create_user('other', 'test.@ewb.ca', 'password')
        self.client.login('other', 'password')
        response = self.client.post(reverse('topic_delete', kwargs={'topic_id': topic_id}))

        # make sure we get a redirect
        self.assertEquals(response.status_code, 302)
        # make sure the topic is still there
        self.assertEquals(gt, GroupTopic.objects.get(topic_id))
