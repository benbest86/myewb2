from django.test import TestCase

from django.contrib.auth.models import User, AnonymousUser

from base_groups.models import BaseGroup, GroupMember, GroupMemberRecord
from base_groups.decorators import *

METHOD_RUN = "The method was run!!"

@group_admin_required()
def group_admin_required_test(request, group_slug):
    return METHOD_RUN

@group_membership_required()
def group_membership_required_test(request, group_slug):
    return METHOD_RUN

@own_member_object_required()
def own_member_object_required_test(request, group_slug, username):
    return METHOD_RUN

@visibility_required()
def visibility_required_test(request, group_slug):
    return METHOD_RUN

class RequestClass:
    user = None
    session = {}
    COOKIES = {}
    META = {}
    def __init__(self, user):
        self.user = user

class TestGroupDecorators(TestCase):
    setup = False
    
    def setUp(self):
        # could use a fixture instead... but i like this better.  easier to edit.
        if not self.setup:
            # create group
            self.group_creator = User.objects.create_user('creator', 'c@ewb.ca')
            self.bg = BaseGroup.objects.create(slug='bg', name='generic base group', creator=self.group_creator)
            self.invisible = BaseGroup.objects.create(slug='bg2', name='generic invisible base group', creator=self.group_creator, visibility='M')
            
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
            
            # and add another random no-body 
            self.user2 = User.objects.create_user('user2', 'user2@ewb.ca')
            
            self.setup = True

    def tearDown(self):
        pass

    def test_group_admin_required(self):
        """
        Test the @group_admin_required decorator
        """
        # creator is an admin...
        self.assertEquals(group_admin_required_test(RequestClass(user=self.group_creator), 'bg'), METHOD_RUN)
        
        # group admin should work
        self.assertEquals(group_admin_required_test(RequestClass(user=self.groupadmin), 'bg'), METHOD_RUN)
        
        # group member should not
        self.assertNotEquals(group_admin_required_test(RequestClass(user=self.member), 'bg'), METHOD_RUN)
        
        # nor should a non-member
        self.assertNotEquals(group_admin_required_test(RequestClass(user=self.user), 'bg'), METHOD_RUN)
        
        # or the guest user!
        self.assertNotEquals(group_admin_required_test(RequestClass(user=AnonymousUser()), 'bg'), METHOD_RUN)

    def test_group_membership_required(self):
        """
        Test the @group_membership_required decorator
        """
        # creator is a member...
        self.assertEquals(group_membership_required_test(RequestClass(user=self.group_creator), 'bg'), METHOD_RUN)
        
        # group admin should work
        self.assertEquals(group_membership_required_test(RequestClass(user=self.groupadmin), 'bg'), METHOD_RUN)
        
        # group member should work
        self.assertEquals(group_membership_required_test(RequestClass(user=self.member), 'bg'), METHOD_RUN)
        
        # but non-member not
        self.assertNotEquals(group_membership_required_test(RequestClass(user=self.user), 'bg'), METHOD_RUN)
        
        # or the guest user!
        self.assertNotEquals(group_membership_required_test(RequestClass(user=AnonymousUser()), 'bg'), METHOD_RUN)

    def test_own_member_object_required(self):
        """
        Test the @own_member_object_required decorator
        """
        # creator always returns true
        self.assertEquals(own_member_object_required_test(RequestClass(user=self.group_creator), 'bg', self.group_creator.username), METHOD_RUN)
        self.assertEquals(own_member_object_required_test(RequestClass(user=self.group_creator), 'bg', self.user2.username), METHOD_RUN)
        
        # group admin should always work
        self.assertEquals(own_member_object_required_test(RequestClass(user=self.groupadmin), 'bg', self.groupadmin.username), METHOD_RUN)
        self.assertEquals(own_member_object_required_test(RequestClass(user=self.groupadmin), 'bg', self.user2.username), METHOD_RUN)
        
        # group member does not have override
        self.assertEquals(own_member_object_required_test(RequestClass(user=self.member), 'bg', self.member.username), METHOD_RUN)
        self.assertNotEquals(own_member_object_required_test(RequestClass(user=self.member), 'bg', self.user2.username), METHOD_RUN)
        
        # same with non-member
        self.assertEquals(own_member_object_required_test(RequestClass(user=self.user), 'bg', self.user.username), METHOD_RUN)
        self.assertNotEquals(own_member_object_required_test(RequestClass(user=self.user), 'bg', self.user2.username), METHOD_RUN)
        
        # for the guest user
        self.assertNotEquals(own_member_object_required_test(RequestClass(user=AnonymousUser()), 'bg', self.user2.username), METHOD_RUN)

    def test_visibility_required(self):
        """
        Test the @visibility_required decorator
        """
        # creator can always see the group
        self.assertEquals(visibility_required_test(RequestClass(user=self.group_creator), 'bg'), METHOD_RUN)
        self.assertEquals(visibility_required_test(RequestClass(user=self.group_creator), 'bg2'), METHOD_RUN)
        
        # group admin can see the group
        self.assertEquals(visibility_required_test(RequestClass(user=self.groupadmin), 'bg'), METHOD_RUN)
        self.assertEquals(visibility_required_test(RequestClass(user=self.groupadmin), 'bg2'), METHOD_RUN)
        
        # group member can see the group
        self.assertEquals(visibility_required_test(RequestClass(user=self.member), 'bg'), METHOD_RUN)
        self.assertEquals(visibility_required_test(RequestClass(user=self.member), 'bg2'), METHOD_RUN)
        
        # non-member can see visible group, but not the invisible group
        self.assertEquals(visibility_required_test(RequestClass(user=self.user), 'bg'), METHOD_RUN)
        self.assertNotEquals(visibility_required_test(RequestClass(user=self.user), 'bg2'), METHOD_RUN)
        
        # ditto the guest
        self.assertEquals(visibility_required_test(RequestClass(user=AnonymousUser()), 'bg'), METHOD_RUN)
        self.assertNotEquals(visibility_required_test(RequestClass(user=AnonymousUser()), 'bg2'), METHOD_RUN)
