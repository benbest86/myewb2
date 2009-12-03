from django.contrib.auth.models import User, AnonymousUser
from django.test import TestCase
from django.test.client import Client

from base_groups.models import BaseGroup
from group_topics.models import GroupTopic
from tagging.models import Tag, TaggedItem

class TestPost(TestCase):
    """ Ensure the posts that a tag listing returns are all visible """
    
    def setUp(self):
        self.u = User.objects.create_user('user', 'user@ewb.ca', 'password')
        self.u.save()
        
        self.u2 = User.objects.create_user('user2', 'user2@ewb.ca', 'password')
        self.u2.save()
        
        self.u3 = User.objects.create_user('user3', 'user3@ewb.ca', 'password')
        self.u3.save()
        
        self.bg = BaseGroup.objects.create(slug='bg', name='a base group', creator=self.u, visibility='E')
        self.bg.add_member(self.u2)
        self.bg.save()
        
        self.post = GroupTopic.objects.create(title="publicpost",
                                              body="some test text.",
                                              group=self.bg,
                                              creator=self.u)
        
        self.tag = Tag.objects.create(name='testtag')
        self.item = TaggedItem.objects.create(tag=self.tag, object=self.post)
    
        self.bg2 = BaseGroup.objects.create(slug='bg2', name='a private base group', creator=self.u, visibility='M')
        self.bg2.add_member(self.u2)
        self.bg2.save()
        
        self.post2 = GroupTopic.objects.create(title="privatepost",
                                               body="some more test text.",
                                               group=self.bg2,
                                               creator=self.u)
        
        self.item2 = TaggedItem.objects.create(tag=self.tag, object=self.post2)
    
    def test_public_group(self):
        """ ensure posts to a public group appear on tag list """

        c = self.client 

        # guest
        response = c.get("/tags/testtag/")
        self.assertContains(response, "publicpost")
        
        # creator
        c.login(username='user', password='password')
        response = c.get("/tags/testtag/")
        self.assertContains(response, "publicpost")
        c.logout()
        
        # group member
        c.login(username='user2', password='password')
        response = c.get("/tags/testtag/")
        self.assertContains(response, "publicpost")
        c.logout()

        # non-member
        c.login(username='user3', password='password')
        response = c.get("/tags/testtag/")
        self.assertContains(response, "publicpost")
        c.logout()
       
    def test_private_group(self):
        """ ensure posts to a private group only show up for group members """
        
        c = self.client 

        # guest
        response = c.get("/tags/testtag/")
        self.assertNotContains(response, "privatepost")
        
        # creator
        c.login(username='user', password='password')
        response = c.get("/tags/testtag/")
        self.assertContains(response, "privatepost")
        c.logout()
        
        # group member
        c.login(username='user2', password='password')
        response = c.get("/tags/testtag/")
        self.assertContains(response, "privatepost")
        c.logout()

        # non-member
        c.login(username='user3', password='password')
        response = c.get("/tags/testtag/")
        self.assertNotContains(response, "privatepost")
        c.logout()
