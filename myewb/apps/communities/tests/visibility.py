from django.test import TestCase
from django.contrib.auth.models import User, AnonymousUser

from base_groups.models import BaseGroup, GroupMember
from communities.models import Community

class TestVisibility(TestCase):
    def setUp(self):

        # an admin of the parent group, non-member of the child group
        self.u = User.objects.create_user('user', 'user@ewb.ca', 'password')
        
        # a member (non-admin) of the parent group, non-member of the child group
        self.u2 = User.objects.create_user('user2', 'user2@ewb.ca', 'password')
        
        # admin of the child group
        self.u3 = User.objects.create_user('user3', 'user3@ewb.ca', 'password')
        
        # member (non-admin) of the child group
        self.u4 = User.objects.create_user('user4', 'user4@ewb.ca', 'password')
        
        # random nobody
        self.u5 = User.objects.create_user('user5', 'user5@ewb.ca', 'password')
        
        # set up the groups & memberships...s
        self.parent = BaseGroup.objects.create(slug='bg',
                                               name='a base group',
                                               creator=self.u,
                                               visibility='E')
        m = GroupMember(group=self.parent,
                        user=self.u2,
                        is_admin=False)
        m.save()
        
        self.child = Community.objects.create(slug='community',
                                              name='a community',
                                              creator=self.u3,
                                              parent=self.parent,
                                              visibility='M')
        m2 = GroupMember(group=self.child,
                         user=self.u4,
                         is_admin=False)
        m2.save()
        

    def test_parent_permissions(self):
        """
        Ensure admins of a parent group are implicit admins of children
        """

        self.assertTrue(self.child.is_visible(self.u))
        self.assertTrue(self.child.user_is_admin(self.u))
        
        # but members (non-admins) of the parent don't have permissions on the child...
        self.assertFalse(self.child.is_visible(self.u2))
        self.assertFalse(self.child.user_is_admin(self.u2))
    
    def test_visible_children(self):
        """
        Ensure the "get_visible_children" function is working
        """
        
        # get_visible_children returns a list of BaseGroups, not communities...
        childgroup = BaseGroup.objects.get(slug=self.child.slug)

        self.assertTrue(childgroup in self.parent.get_visible_children(self.u))
        self.assertFalse(childgroup in self.parent.get_visible_children(self.u2))
        self.assertTrue(childgroup in self.parent.get_visible_children(self.u3))
        self.assertTrue(childgroup in self.parent.get_visible_children(self.u4))
        self.assertFalse(childgroup in self.parent.get_visible_children(self.u5))

