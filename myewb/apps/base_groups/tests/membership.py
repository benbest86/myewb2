from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from base_groups.models import BaseGroup, GroupMember, PendingMember, \
        InvitationToJoinGroup, RequestToJoinGroup, GroupMemberRecord

class TestPendingMembers(TestCase):
    """
    Tests common functionality in PendingMember class.
    """
    
    def setUp(self):
        # create base group creator
        # create base group
        self.creator = User.objects.create_user(username='creator', email='creator@ewb.ca')
        self.bg = BaseGroup.objects.create(slug='bg', description='a test base_group', creator=self.creator)

    def test_accept(self):
        other_user = User.objects.create(username='other_user', email='other@ewb.ca')
        pm = PendingMember.objects.create(user=other_user, group=self.bg, message='to test out membership.')
        self.assertFalse(self.bg.user_is_member(other_user))
        pm.accept()
        self.assertTrue(self.bg.user_is_member(other_user))
        self.assertEquals(0, other_user.pending_memberships.count())

    def test_reject(self):
        other_user = User.objects.create(username='other_user', email='other@ewb.ca')
        pm = InvitationToJoinGroup.objects.create(user=other_user, group=self.bg, message='to test out membership.')
        self.assertFalse(self.bg.user_is_member(other_user))
        pm.reject()
        self.assertFalse(self.bg.user_is_member(other_user))
        self.assertEquals(0, other_user.pending_memberships.count())

class TestInvitations(TestCase):
    """
    Tests to ensure an invitation can be created and
    that the is_invited property works correctly.
    """
    
    def setUp(self):
        # create base group creator
        # create base group
        self.creator = User.objects.create_user(username='creator', email='creator@ewb.ca')
        self.bg = BaseGroup.objects.create(slug='bg', description='a test base_group', creator=self.creator)

    def test_invite_user(self):
        other_user = User.objects.create(username='other_user', email='other@ewb.ca')
        self.assertFalse(self.bg.user_is_pending_member(other_user))
        InvitationToJoinGroup.objects.create(user=other_user, group=self.bg, message='to test out membership.')
        self.assertTrue(self.bg.user_is_pending_member(other_user))
        pm = other_user.pending_memberships.get()
        self.assertTrue(pm.is_invited)
        self.assertFalse(pm.is_requested)

class TestRequests(TestCase):
    """
    Tests to ensure a request can be created and
    that the is_requested property works correctly.
    """
    
    def setUp(self):
        # create base group creator
        # create base group
        self.creator = User.objects.create_user(username='creator', email='creator@ewb.ca')
        self.bg = BaseGroup.objects.create(slug='bg', description='a test base_group', creator=self.creator)

    def test_invite_user(self):
        other_user = User.objects.create(username='other_user', email='other@ewb.ca')
        self.assertFalse(self.bg.user_is_pending_member(other_user))
        RequestToJoinGroup.objects.create(user=other_user, group=self.bg, message='to test out membership.')
        self.assertTrue(self.bg.user_is_pending_member(other_user))
        pm = other_user.pending_memberships.get()
        self.assertFalse(pm.is_invited)
        self.assertTrue(pm.is_requested)

