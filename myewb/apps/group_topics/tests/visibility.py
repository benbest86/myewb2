import re

from django.contrib.auth.models import User, AnonymousUser
from django.test import TestCase
from django.test.client import Client

from base_groups.models import BaseGroup
from group_topics.models import GroupTopic
from tagging.models import Tag, TaggedItem

class TestVisibility(TestCase):
    """ Test all aspects of post visibility """
    
    def setUp(self):
        self.creator = User.objects.create_user('creator', 'user@ewb.ca', 'password')
        self.creator.save()
        
        self.member = User.objects.create_user('member', 'user2@ewb.ca', 'password')
        self.member.save()
        
        self.nonmember = User.objects.create_user('nonmember', 'user3@ewb.ca', 'password')
        self.nonmember.save()
        
        self.admin = User.objects.create_user('admin', 'user4@ewb.ca', 'password')
        self.admin.is_superuser = True
        self.admin.save()
        
        self.publicgrp = BaseGroup.objects.create(slug='publicgrp',
                                                  name='a public group',
                                                  creator=self.member,
                                                  model='BaseGroup',
                                                  visibility='E')
        self.privategrp = BaseGroup.objects.create(slug='privategrp',
                                                   name='a private group',
                                                   creator=self.member,
                                                   model='BaseGroup',
                                                   visibility='M')
        
        self.publicpost = GroupTopic.objects.create(title="publicpost",
                                                    body="some test text.",
                                                    group=self.publicgrp,
                                                    creator=self.creator)
        
        self.privatepost = GroupTopic.objects.create(title="privatepost",
                                                     body="some more test text.",
                                                     group=self.privategrp,
                                                     creator=self.creator)

        self.tag = Tag.objects.create(name='testtag')
        self.item1 = TaggedItem.objects.create(tag=self.tag, object=self.publicpost)
        self.item2 = TaggedItem.objects.create(tag=self.tag, object=self.privatepost)
    
    def test_guest(self):
        """ check guest user's visibility """
        
        c = self.client

        # aggregate listing on front page
        response = c.get("/")
        self.assertContains(response, "publicpost")
        self.assertNotContains(response, "privatepost")
        
        # aggregate listing by tag
        response = c.get("/tags/testtag/")
        self.assertContains(response, "publicpost")
        self.assertNotContains(response, "privatepost")

        # public post is visible by direct URL
        response = c.get("/posts/%d/" % self.publicpost.pk)
        self.assertContains(response, "publicpost")
        
        # private post is not visible by direct URL
        response = c.get("/posts/%d/" % self.privatepost.pk)
        #self.assertNotContains(response, "privatepost")
        self.assertEqual(response.status_code, 403)
        
    def test_creator(self):
        """ check post creator's visibility """
        c = self.client
        c.login(username='creator', password='password')

        # aggregate listing on front page
        response = c.get("/")
        self.assertNotContains(response, "publicpost")
        self.assertNotContains(response, "privatepost")
        # yes, those are intentional assertNotContains - since the post creator
        # isn't a member of the group...
        
        # aggregate listing by tag
        response = c.get("/tags/testtag/")
        self.assertContains(response, "publicpost")
        self.assertNotContains(response, "privatepost")
        # yes, those are intentional assertNotContains - since the post creator
        # isn't a member of the group...

        # public post is visible by direct URL
        response = c.get("/posts/%d/" % self.publicpost.pk)
        self.assertContains(response, "publicpost")
        
        # private post is visible by direct URL
        response = c.get("/posts/%d/" % self.privatepost.pk)
        self.assertContains(response, "privatepost")
        
        c.logout()
        
    def test_member(self):
        """ check group member's visibility """
        c = self.client
        c.login(username='member', password='password')

        # aggregate listing on front page
        response = c.get("/")
        self.assertContains(response, "publicpost")
        self.assertContains(response, "privatepost")
        
        # aggregate listing by tag
        response = c.get("/tags/testtag/")
        self.assertContains(response, "publicpost")
        self.assertContains(response, "privatepost")

        # public post is visible by direct URL
        response = c.get("/posts/%d/" % self.publicpost.pk)
        self.assertContains(response, "publicpost")
        
        # private post is visible by direct URL
        response = c.get("/posts/%d/" % self.privatepost.pk)
        self.assertContains(response, "privatepost")
        
        c.logout()
        
    def test_nonmember(self):
        """ check non-member's visibility """
        c = self.client
        c.login(username='nonmember', password='password')

        # aggregate listing on front page
        response = c.get("/")
        # see TODO question in group_topics.views:161
        self.assertNotContains(response, "publicpost")
        self.assertNotContains(response, "privatepost")
        
        # aggregate listing by tag
        response = c.get("/tags/testtag/")
        self.assertContains(response, "publicpost")
        self.assertNotContains(response, "privatepost")

        # public post is visible by direct URL
        response = c.get("/posts/%d/" % self.publicpost.pk)
        self.assertContains(response, "publicpost")
        
        # private post is not visible by direct URL
        response = c.get("/posts/%d/" % self.privatepost.pk)
        #self.assertNotContains(response, "privatepost")
        self.assertEqual(response.status_code, 403)
        
        c.logout()
        
    def test_admin(self):
        """ check admin's visibility """
        c = self.client
        c.login(username='admin', password='password')

        # aggregate listing on front page
        response = c.get("/")
        # see TODO question in group_topics.views:161
        # (assuming no admin-o-vision)
        self.assertNotContains(response, "publicpost")
        self.assertNotContains(response, "privatepost")
        
        # aggregate listing by tag
        response = c.get("/tags/testtag/")
        self.assertContains(response, "publicpost")
        self.assertNotContains(response, "privatepost")
        # (again, no admin-o-vision)

        # public post is visible by direct URL
        response = c.get("/posts/%d/" % self.publicpost.pk)
        self.assertContains(response, "publicpost")
        
        # private post is visible by direct URL
        response = c.get("/posts/%d/" % self.privatepost.pk)
        self.assertContains(response, "privatepost")
        
        c.logout()
        
    def test_feeds(self):
        """ test RSS feed visibility """
        # membership/etc doesn't exist, as all RSS feeds are guest-only

        c = self.client 

        # public group
        response = c.get("/feeds/posts/publicgrp/")
        self.assertContains(response, "publicpost")
       
        # private group (not visible)
        response = c.get("/feeds/posts/privategrp/")
        #self.assertNotContains(response, "privatepost")
        self.assertEqual(response.status_code, 403)
       
        # only public posts show in the aggregate RSS feed
        response = c.get("/feeds/posts/all/")
        self.assertContains(response, "publicpost")
        self.assertNotContains(response, "privatepost")
