import re

from django.contrib.auth.models import User, AnonymousUser
from django.test import TestCase
from django.test.client import Client

from base_groups.models import BaseGroup
from group_topics.models import GroupTopic

class TestPost(TestCase):
    """ These test are somewhat redundant, assuming BaseGroup.is_visible is
        implemented and tested properly... but just in case."""
    
    def setUp(self):
        self.u = User.objects.create_user('user', 'user@ewb.ca', 'password')
        self.u.save()
        
        self.u2 = User.objects.create_user('user2', 'user2@ewb.ca', 'password')
        self.u2.save()
        
        self.u3 = User.objects.create_user('user3', 'user3@ewb.ca', 'password')
        self.u3.save()
        
        self.bg = BaseGroup.objects.create(slug='bg', name='a base group', creator=self.u)
        self.bg.add_member(self.u2)
        self.bg.save()
        
        self.post = GroupTopic.objects.create(title="test",
                                              body="some test text.",
                                              group=self.bg,
                                              creator=self.u)
    
    def test_public_group(self):
        """ ensure everyone can see posts to a public group """
        
        self.bg.visibility = 'E'
        self.bg.save()
        c = self.client 

        # guest
        response = c.get("/posts/%d/" % self.post.pk)
        self.assertContains(response, "test")
        
        # creator
        c.login(username='user', password='password')
        response = c.get("/posts/%d/" % self.post.pk)
        self.assertContains(response, "test")
        c.logout()
        
        # group member
        c.login(username='user2', password='password')
        response = c.get("/posts/%d/" % self.post.pk)
        self.assertContains(response, "test")
        c.logout()

        # non-member
        c.login(username='user3', password='password')
        response = c.get("/posts/%d/" % self.post.pk)
        self.assertContains(response, "test")
        c.logout()
       
    def test_private_group(self):
        """ ensure only members can see posts to a private group """
        
        self.bg.visibility = 'M'
        self.bg.save()
        c = self.client 

        # guest
        response = c.get("/posts/%d/" % self.post.pk)
        #self.assertNotContains(response, "test")
        self.assertEqual(response.status_code, 403)
        
        # creator
        c.login(username='user', password='password')
        response = c.get("/posts/%d/" % self.post.pk)
        self.assertContains(response, "test")
        c.logout()
        
        # group member
        c.login(username='user2', password='password')
        response = c.get("/posts/%d/" % self.post.pk)
        self.assertContains(response, "test")
        c.logout()

        # non-member
        c.login(username='user3', password='password')
        response = c.get("/posts/%d/" % self.post.pk)
        #self.assertNotContains(response, "test")
        self.assertEqual(response.status_code, 403)
        c.logout()
        
class TestListing(TestCase):
    """ Test the main post list, to ensure only visible posts are on it"""
    
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
    
        self.bg2 = BaseGroup.objects.create(slug='bg2', name='another base group', creator=self.u, visibility='M')
        self.bg2.add_member(self.u2)
        self.bg2.save()
        
        self.post2 = GroupTopic.objects.create(title="privatepost",
                                               body="some more test text.",
                                               group=self.bg2,
                                               creator=self.u)
    
    def test_public_group(self):
        """ ensure everyone can see posts to a public group """
        
        c = self.client 

        # guest
        response = c.get("/")
        self.assertContains(response, "publicpost")
        
        # creator
        c.login(username='user', password='password')
        response = c.get("/")
        self.assertContains(response, "publicpost")
        c.logout()
        
        # group member
        c.login(username='user2', password='password')
        response = c.get("/")
        self.assertContains(response, "publicpost")
        c.logout()

        # non-member
        c.login(username='user3', password='password')
        response = c.get("/")
        # see TODO question in group_topics.views line 161
        self.assertNotContains(response, "publicpost")
        c.logout()
       
    def test_private_group(self):
        """ ensure only members can see posts to a private group """
        
        c = self.client 

        # guest
        response = c.get("/")
        self.assertNotContains(response, "privatepost")
        
        # creator
        c.login(username='user', password='password')
        response = c.get("/")
        self.assertContains(response, "privatepost")
        c.logout()
        
        # group member
        c.login(username='user2', password='password')
        response = c.get("/")
        self.assertContains(response, "privatepost")
        c.logout()

        # non-member
        c.login(username='user3', password='password')
        response = c.get("/")
        self.assertNotContains(response, "privatepost")
        c.logout()
        
class TestFeeds(TestCase):
    """ Test the post RSS feeds, to ensure only visible posts are on it"""
    
    def setUp(self):
        self.u = User.objects.create_user('user', 'user@ewb.ca', 'password')
        self.u.save()
        
        self.bg = BaseGroup.objects.create(slug='bg', name='a base group', creator=self.u, visibility='E', model='BaseGroup')
        self.bg.save()
        
        self.post = GroupTopic.objects.create(title="publicpost",
                                              body="some test text.",
                                              group=self.bg,
                                              creator=self.u)
    
        self.bg2 = BaseGroup.objects.create(slug='bg2', name='another base group', creator=self.u, visibility='M', model='BaseGroup')
        self.bg2.save()
        
        self.post2 = GroupTopic.objects.create(title="privatepost",
                                               body="some more test text.",
                                               group=self.bg2,
                                               creator=self.u)
    
    def test_public_group(self):
        """ ensure feed of a public group is visible """
        
        c = self.client 

        response = c.get("/feeds/posts/bg/")
        self.assertContains(response, "publicpost")
       
    def test_private_group(self):
        """ ensure feed of a private group is not visible """
        
        c = self.client 

        response = c.get("/feeds/posts/bg2/")
        #self.assertNotContains(response, "privatepost")
        self.assertEqual(response.status_code, 403)
       
    def test_listing(self):
        """ ensure only public posts show in the aggregate RSS feed """
        
        c = self.client 

        response = c.get("/feeds/posts/all/")
        self.assertContains(response, "publicpost")
        self.assertNotContains(response, "privatepost")
        