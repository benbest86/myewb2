from django.test import TestCase

from django.contrib.auth.models import User, AnonymousUser

from base_groups.models import BaseGroup, GroupMember, GroupMemberRecord
from base_groups.helpers import *

class TestGroupHelpers(TestCase):
    setup = False
    
    def setUp(self):
        # could use a fixture instead... but i like this better.  easier to edit.
        if not self.setup:
            # create group
            self.group_creator = User.objects.create_user('creator', 'c@ewb.ca')
            self.bg = BaseGroup.objects.create(slug='bg', name='generic base group', description='description1', creator=self.group_creator, model='Network')
            self.invisible = BaseGroup.objects.create(slug='bg2', name='generic invisible base group', description='description2', creator=self.group_creator, visibility='M')
            
            # add a group admin
            self.groupadmin = User.objects.create_user('groupadmin', 'groupadmin@ewb.ca')
            self.bg.add_member(self.groupadmin)
            self.invisible.add_member(self.groupadmin)
            gmember = GroupMember.objects.get(user=self.groupadmin, group=self.bg)
            gmember.is_admin = True
            gmember.save()          # should we create BaseGroup.add_admin()?? but that would require refactoring all the membership forms...
            self.invisible.add_member(self.groupadmin)
            gmember = GroupMember.objects.get(user=self.groupadmin, group=self.invisible)
            gmember.is_admin = True
            gmember.save()          # should we create BaseGroup.add_admin()?? but that would require refactoring all the membership forms...
            
            # add a normal group member
            self.member = User.objects.create_user('member', 'member@ewb.ca')
            self.bg.add_member(self.member)
            self.invisible.add_member(self.member)
            
            # and add a regular non-member user
            self.user = User.objects.create_user('user', 'user@ewb.ca')
            
            # and make someone a member of one group, but not the other 
            self.user2 = User.objects.create_user('user2', 'user2@ewb.ca')
            self.bg.add_member(self.user2)
            
            # and a site admin
            self.siteadmin = User.objects.create_user('siteadmin', 'siteadmin@ewb.ca')
            self.siteadmin.is_staff = True
            self.siteadmin.save()
            
            
            self.setup = True

    def tearDown(self):
        pass

    def test_group_search_filter(self):
        """
        If given search terms, this should return a filter based on name and description
        """
        groups = group_search_filter(BaseGroup.objects.all(), None)
        self.assertTrue(list(groups).count(self.bg))
        self.assertTrue(list(groups).count(self.invisible))
        
        groups = group_search_filter(BaseGroup.objects.all(), 'generic')
        self.assertTrue(list(groups).count(self.bg))
        self.assertTrue(list(groups).count(self.invisible))
        
        groups = group_search_filter(BaseGroup.objects.all(), 'invisible')
        self.assertFalse(list(groups).count(self.bg))
        self.assertTrue(list(groups).count(self.invisible))
        
        groups = group_search_filter(BaseGroup.objects.all(), 'description')
        self.assertTrue(list(groups).count(self.bg))
        self.assertTrue(list(groups).count(self.invisible))
        
        groups = group_search_filter(BaseGroup.objects.all(), 'description1')
        self.assertTrue(list(groups).count(self.bg))
        self.assertFalse(list(groups).count(self.invisible))
        
    def test_get_counts(self):
        groups = get_counts(BaseGroup.objects.all(), BaseGroup)
        for g in groups:
            if g.slug == 'bg':
                self.assertEquals(g.member_count, 4)
            if g.slug == 'invisible':
                self.assertEquals(g.member_count, 3)
            self.assertEquals(g.topic_count, 0)
            
    def test_enforce_visibility(self):
        # group creator can see
        groups = enforce_visibility(BaseGroup.objects.all(), self.group_creator)
        self.assertTrue(list(groups).count(self.bg))
        self.assertTrue(list(groups).count(self.invisible))

        # group admin can see
        groups = enforce_visibility(BaseGroup.objects.all(), self.groupadmin)
        self.assertTrue(list(groups).count(self.bg))
        self.assertTrue(list(groups).count(self.invisible))
        
        # group member can see
        groups = enforce_visibility(BaseGroup.objects.all(), self.member)
        self.assertTrue(list(groups).count(self.bg))
        self.assertTrue(list(groups).count(self.invisible))

        # non-member can see public group only
        groups = enforce_visibility(BaseGroup.objects.all(), self.user)
        self.assertTrue(list(groups).count(self.bg))
        self.assertFalse(list(groups).count(self.invisible))
        
        # ditto with guest
        groups = enforce_visibility(BaseGroup.objects.all(), AnonymousUser())
        self.assertTrue(list(groups).count(self.bg))
        self.assertFalse(list(groups).count(self.invisible))
        
    def test_get_valid_parents(self):
        groups = get_valid_parents(self.user2)
        self.assertTrue(list(groups).count(self.bg))
        self.assertFalse(list(groups).count(self.invisible))
        
        groups = get_valid_parents(self.user2, self.bg)
        self.assertFalse(list(groups).count(self.bg))
        self.assertFalse(list(groups).count(self.invisible))
        
    def test_user_can_adminovision(self):
        self.assertFalse(user_can_adminovision(self.group_creator))
        self.assertFalse(user_can_adminovision(self.groupadmin))
        self.assertFalse(user_can_adminovision(self.member))
        self.assertFalse(user_can_adminovision(self.user))
        self.assertFalse(user_can_adminovision(AnonymousUser()))
        self.assertTrue(user_can_adminovision(self.siteadmin))

    def test_user_can_execovision(self):
        self.assertTrue(user_can_execovision(self.group_creator))
        self.assertTrue(user_can_execovision(self.groupadmin))
        self.assertFalse(user_can_execovision(self.member))
        self.assertFalse(user_can_execovision(self.user))
        self.assertFalse(user_can_execovision(AnonymousUser()))
        self.assertFalse(user_can_execovision(self.siteadmin)) # because they can adminovision instad
        
