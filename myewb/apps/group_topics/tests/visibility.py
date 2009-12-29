from django.contrib.auth.models import User, AnonymousUser
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.test.client import Client

from base_groups.models import BaseGroup, GroupMember
from networks.models import Network
from group_topics.models import GroupTopic
from tagging.models import Tag, TaggedItem

class VisibilityBaseTest(TestCase):
    """
    Base class with common setup function.
    """
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
        
        self.grpadmin = User.objects.create_user('grpadmin', 'user5@ewb.ca', 'password')
        self.grpadmin.save()
        
        self.publicgrp = Network.objects.create(slug='publicgrp',
                                                name='a public group',
                                                creator=self.member,
                                                visibility='E')
        self.privategrp = BaseGroup.objects.create(slug='privategrp',
                                                   name='a private group',
                                                   creator=self.member,
                                                   model='Community',
                                                   visibility='M',
                                                   parent=self.publicgrp)
        
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
        
        m = GroupMember(user=self.grpadmin,
                        group=self.publicgrp,
                        is_admin=True)
        m.save()

        self.gtopic = ContentType.objects.get(app_label="group_topics", model="grouptopic")

class TestVisibility(VisibilityBaseTest):
    """ Test all aspects of post visibility """
    
    
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
        
        # aggregate listing by user
        response = c.get("/posts/user/%s/" % self.creator.username)
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
        self.assertContains(response, "publicpost")
        self.assertNotContains(response, "privatepost")
        # yes, those are intentional assertNotContains - since the post creator
        # isn't a member of the group...
        
        # aggregate listing by tag
        response = c.get("/tags/testtag/")
        self.assertContains(response, "publicpost")
        self.assertNotContains(response, "privatepost")
        # yes, those are intentional assertNotContains - since the post creator
        # isn't a member of the group...

        # aggregate listing by user
        response = c.get("/posts/user/%s/" % self.creator.username)
        self.assertContains(response, "publicpost")
        self.assertContains(response, "privatepost")

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

        # aggregate listing by user
        response = c.get("/posts/user/%s/" % self.creator.username)
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
        self.assertContains(response, "publicpost")
        self.assertNotContains(response, "privatepost")
        
        # aggregate listing by tag
        response = c.get("/tags/testtag/")
        self.assertContains(response, "publicpost")
        self.assertNotContains(response, "privatepost")

        # aggregate listing by user
        response = c.get("/posts/user/%s/" % self.creator.username)
        self.assertContains(response, "publicpost")
        self.assertNotContains(response, "privatepost")

        # public post is visible by direct URL
        response = c.get("/posts/%d/" % self.publicpost.pk)
        self.assertContains(response, "publicpost")
        
        # private post is not visible by direct URL
        response = c.get("/posts/%d/" % self.privatepost.pk)
        #self.assertNotContains(response, "privatepost")
        self.assertEqual(response.status_code, 403)

        # private post cannot be edited by nonmember
        response = c.post("/posts/%d/" % self.privatepost.pk, {'title': 'My new title', 'body': 'hackers for life'})
        self.assertEqual(response.status_code, 403)

        
        c.logout()
        
    def test_admin(self):
        """ check admin's visibility, assumes no admin-o-vision """
        c = self.client
        c.login(username='admin', password='password')

        # aggregate listing on front page
        response = c.get("/")
        self.assertContains(response, "publicpost")
        self.assertNotContains(response, "privatepost")
        
        # aggregate listing by tag
        response = c.get("/tags/testtag/")
        self.assertContains(response, "publicpost")
        self.assertNotContains(response, "privatepost")
        
        # aggregate listing by user
        response = c.get("/posts/user/%s/" % self.creator.username)
        self.assertContains(response, "publicpost")
        self.assertNotContains(response, "privatepost")
        
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

class TestVisibilityManagerFunctions(VisibilityBaseTest):
    """
    Tests the visibility manager functions.
    """
    def test_anon_visibility(self):
        public = GroupTopic.objects.visible()
        self.assertTrue(self.publicpost in public)
        self.assertTrue(self.privatepost not in public)

    def test_public_with_anon_user(self):
        public = GroupTopic.objects.visible(AnonymousUser())
        self.assertTrue(self.publicpost in public)

    def test_public_with_user(self):
        visible_to_creator = GroupTopic.objects.visible(self.creator)
        self.assertTrue(self.publicpost in visible_to_creator)

    def test_private_with_authorized_user(self):
        visible_to_member = GroupTopic.objects.visible(self.member)
        self.assertTrue(self.privatepost in visible_to_member)

    def test_private_with_unauthorized_user(self):
        visible_to_nonmember = GroupTopic.objects.visible(self.nonmember)
        self.assertTrue(self.privatepost not in visible_to_nonmember)
        
    def test_public_with_admin(self):
        visible_to_admin = GroupTopic.objects.visible(self.admin)
        self.assertTrue(self.publicpost in visible_to_admin)
        
    def test_private_with_admin(self):
        self.admin.get_profile().adminovision = False
        visible_to_admin = GroupTopic.objects.visible(self.admin)
        self.assertTrue(self.privatepost not in visible_to_admin)

    def test_private_with_adminovision(self):
        self.admin.get_profile().adminovision = True
        visible_to_admin = GroupTopic.objects.visible(self.admin)
        self.assertTrue(self.privatepost in visible_to_admin)
        
    def test_private_with_exec(self):
        self.grpadmin.get_profile().adminovision = False
        visible_to_admin = GroupTopic.objects.visible(self.grpadmin)
        self.assertTrue(self.privatepost not in visible_to_admin)

    def test_private_with_execovision(self):
        self.grpadmin.get_profile().adminovision = True
        visible_to_admin = GroupTopic.objects.visible(self.grpadmin)
        self.assertTrue(self.privatepost in visible_to_admin)
        
    def test_private_with_execovision2(self):
        # ensure someone with execovision access only has that power in their 
        # own group, not in all groups =)
        publicgrp2 = Network.objects.create(slug='publicgrp2',
                                             name='a public group2',
                                             creator=self.member,
                                             visibility='E')
        privategrp2 = BaseGroup.objects.create(slug='privategrp2',
                                              name='a private group2',
                                              creator=self.member,
                                              model='Community',
                                              visibility='M',
                                              parent=publicgrp2)
        
        privatepost2 = GroupTopic.objects.create(title="privatepost2",
                                                body="some more test text2.",
                                                group=privategrp2,
                                                creator=self.creator)

        self.grpadmin.get_profile().adminovision = True
        visible_to_admin = GroupTopic.objects.visible(self.grpadmin)
        self.assertFalse(privatepost2 in visible_to_admin)
        
        # but. because i'm paranoid.  a publicgrp2 admin *can* see privatepost2
        # and can't see privatepost.
        grpadmin2 = User.objects.create_user('grpadmin2', 'grpadmin2@ewb.ca', 'password')
        grpadmin2.save()
        
        m2 = GroupMember(user=grpadmin2,
                        group=publicgrp2,
                        is_admin=True)
        m2.save()
        
        grpadmin2.get_profile().adminovision = True
        visible_to_admin = GroupTopic.objects.visible(grpadmin2)
        self.assertTrue(privatepost2 in visible_to_admin)
        self.assertFalse(self.privatepost in visible_to_admin)
        
        # and i'm way too paranoid.  if you're an admin of two networks...
        m3 = GroupMember(user=grpadmin2,
                        group=self.publicgrp,
                        is_admin=True)
        m3.save()
        
        visible_to_admin = GroupTopic.objects.visible(grpadmin2)
        self.assertTrue(privatepost2 in visible_to_admin)
        self.assertTrue(self.privatepost in visible_to_admin)
        
class TestVisibleFunction(VisibilityBaseTest):
    """
    Tests the is_visible function
    """
    def test_guest(self):
        guest = AnonymousUser()
        self.assertTrue(self.publicpost.is_visible(guest))
        self.assertFalse(self.privatepost.is_visible(guest))
        
    def test_creator(self):
        self.assertTrue(self.publicpost.is_visible(self.creator))
        self.assertTrue(self.privatepost.is_visible(self.creator))
        
    def test_member(self):
        self.assertTrue(self.publicpost.is_visible(self.member))
        self.assertTrue(self.privatepost.is_visible(self.member))
        
    def test_nonmember(self):
        self.assertTrue(self.publicpost.is_visible(self.nonmember))
        self.assertFalse(self.privatepost.is_visible(self.nonmember))
        
    def test_admin(self):
        self.assertTrue(self.publicpost.is_visible(self.admin))
        self.assertTrue(self.privatepost.is_visible(self.admin))
        
class TestComments(VisibilityBaseTest):
    """ Test permissions check on posting replies """
    # this is done here instead of in the mythreadedcomments app because
    # you can't run tests on an app that has no models, apparently.
    
    def test_member(self):
        """ check group member's visibility """
        c = self.client
        c.login(username='member', password='password')

        # posting to public group
        response = c.post("/comments/comment/%d/%d/" % (self.gtopic.pk, self.publicpost.pk),
                          {'comment': 'this is a comment',
                           'attachCount': '0',
                           'next': '/posts/%d/' % (self.publicpost.pk)
                          },
                          follow=True)
        self.assertEquals(response.status_code, 302)        # success is a reidrect...
        
        # posting to private group
        response = c.post("/comments/comment/%d/%d/" % (self.gtopic.pk, self.privatepost.pk),
                          {'comment': 'this is a comment',
                           'attachCount': '0',
                           'next': '/posts/%d/' % (self.privatepost.pk)
                          },
                          follow=True)
        self.assertEquals(response.status_code, 302)        # success is a reidrect...
        
        c.logout()
        
    def test_nonmember(self):
        """ check non-member's visibility """
        c = self.client
        c.login(username='nonmember', password='password')

        # posting to public group
        response = c.post("/comments/comment/%d/%d/" % (self.gtopic.pk, self.publicpost.pk),
                          {'comment': 'this is a comment',
                           'attachCount': '0',
                           'next': '/posts/%d/' % (self.publicpost.pk)
                          },
                          follow=True)
        self.assertEquals(response.status_code, 302)        # success is a reidrect...
        
        # posting to private group
        response = c.post("/comments/comment/%d/%d/" % (self.gtopic.pk, self.privatepost.pk),
                          {'comment': 'this is a comment',
                           'attachCount': '0',
                           'next': '/posts/%d/' % (self.privatepost.pk)
                          },
                          follow=True)
        self.assertEquals(response.status_code, 403)
        
        c.logout()
        
    def test_admin(self):
        """ check admin's visibility """
        c = self.client
        c.login(username='admin', password='password')

        # posting to public group
        response = c.post("/comments/comment/%d/%d/" % (self.gtopic.pk, self.publicpost.pk),
                          {'comment': 'this is a comment',
                           'attachCount': '0',
                           'next': '/posts/%d/' % (self.publicpost.pk)
                          },
                          follow=True)
        self.assertEquals(response.status_code, 302)        # success is a reidrect...
        
        # posting to private group
        response = c.post("/comments/comment/%d/%d/" % (self.gtopic.pk, self.privatepost.pk),
                          {'comment': 'this is a comment',
                           'attachCount': '0',
                           'next': '/posts/%d/' % (self.privatepost.pk)
                          },
                          follow=True)
        self.assertEquals(response.status_code, 302)        # success is a reidrect...
        
        c.logout()
        
