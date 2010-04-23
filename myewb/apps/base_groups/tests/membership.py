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
        pm = InvitationToJoinGroup.objects.create(user=other_user, group=self.bg, message='to test out membership.', invited_by=self.creator)
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
        InvitationToJoinGroup.objects.create(user=other_user, group=self.bg, message='to test out membership.', invited_by=self.creator)
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

class TestMembershipHistory(TestCase):
    """
    Base class with default setUp and tearDown for all other
    membership history tests.
    """

    def setUp(self):
        group_creator = User.objects.create_user('creator', 'c@ewb.ca')
        self.bg = BaseGroup.objects.create(slug='bg', name='generic base group', creator=group_creator)
        self.user = User.objects.create_user('user', 'user@ewb.ca')

    def tearDown(self):
        GroupMemberRecord.objects.all().delete()
        GroupMember.objects.all().delete()
        BaseGroup.objects.all().delete()
        User.objects.all().delete()

    def test_membership_lifecycle(self):
        """
        A general test that puts a user through a common user
        lifecycle and ensures records are created properly.
        """
        # add user to start
        gm = GroupMember.objects.create(user=self.user, group=self.bg)
        self.assertEquals(1, GroupMemberRecord.objects.filter(user=self.user, group=self.bg).count())
        gmr = GroupMemberRecord.objects.latest()
        self.assertFalse(gmr.is_admin)

        # make user admin
        gm.is_admin = True
        gm.admin_title = 'Lowly peon'
        gm.save()
        self.assertEquals(2, GroupMemberRecord.objects.filter(user=self.user, group=self.bg).count())
        gmr = GroupMemberRecord.objects.latest()
        self.assertTrue(gmr.is_admin)
        self.assertEquals('Lowly peon', gmr.admin_title)

        # change admin title
        gm.admin_title = 'President'
        gm.save()
        self.assertEquals(3, GroupMemberRecord.objects.filter(user=self.user, group=self.bg).count())
        gmr = GroupMemberRecord.objects.latest()
        self.assertTrue(gmr.is_admin)
        self.assertEquals('President', gmr.admin_title)

        # remove admin status
        gm.is_admin = False
        gm.admin_title = None
        gm.save()
        self.assertEquals(4, GroupMemberRecord.objects.filter(user=self.user, group=self.bg).count())
        gmr = GroupMemberRecord.objects.latest()
        self.assertFalse(gmr.is_admin)
        self.assertEquals(None, gmr.admin_title)

        # end membership
        gm.delete()
        self.assertEquals(5, GroupMemberRecord.objects.filter(user=self.user, group=self.bg).count())
        gmr = GroupMemberRecord.objects.latest()
        self.assertTrue(gmr.membership_end)

class TestUserDuckPunches(TestCase):
    """
    Testing additions to the User class.
    """

    def test_non_bulk_user(self):
        u = User.objects.create_user(username='fred', email='fred@ewb.ca')
        self.assertFalse(u.is_bulk)

    def test_bulk_user(self):
        u = User.extras.create_bulk_user(email='fred@ewb.ca')
        self.assertTrue(u.is_bulk)
