from django.test import TestCase

from django.contrib.auth.models import User

from base_groups.models import BaseGroup, GroupMember, GroupMemberRecord
from regression import *

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
        # add bulk user to start
        gm = GroupMember.objects.create(user=self.user, group=self.bg, request_status='B')
        self.assertEquals(1, GroupMemberRecord.objects.filter(user=self.user, group=self.bg).count())
        gmr = GroupMemberRecord.objects.latest()
        self.assertEquals('B', gmr.request_status)

        # set user to accepted
        gm.request_status = 'A'
        gm.save()
        self.assertEquals(2, GroupMemberRecord.objects.filter(user=self.user, group=self.bg).count())
        gmr = GroupMemberRecord.objects.latest()
        self.assertEquals('A', gmr.request_status)

        # make user admin
        gm.is_admin = True
        gm.admin_title = 'Lowly peon'
        gm.save()
        self.assertEquals(3, GroupMemberRecord.objects.filter(user=self.user, group=self.bg).count())
        gmr = GroupMemberRecord.objects.latest()
        self.assertEquals('A', gmr.request_status)
        self.assertTrue(gmr.is_admin)
        self.assertEquals('Lowly peon', gmr.admin_title)

        # change admin title
        gm.admin_title = 'President'
        gm.save()
        self.assertEquals(4, GroupMemberRecord.objects.filter(user=self.user, group=self.bg).count())
        gmr = GroupMemberRecord.objects.latest()
        self.assertEquals('A', gmr.request_status)
        self.assertTrue(gmr.is_admin)
        self.assertEquals('President', gmr.admin_title)

        # remove admin status
        gm.is_admin = False
        gm.admin_title = None
        gm.save()
        self.assertEquals(5, GroupMemberRecord.objects.filter(user=self.user, group=self.bg).count())
        gmr = GroupMemberRecord.objects.latest()
        self.assertEquals('A', gmr.request_status)
        self.assertFalse(gmr.is_admin)
        self.assertEquals(None, gmr.admin_title)

        # end membership
        gm.delete()
        self.assertEquals(6, GroupMemberRecord.objects.filter(user=self.user, group=self.bg).count())
        gmr = GroupMemberRecord.objects.latest()
        self.assertEquals('E', gmr.request_status)

class TestUserDuckPunches(TestCase):
    """
    Testing additions to the User class.
    """

    def test_non_bulk_user(self):
        u = User.objects.create_user(username='fred', email='fred@ewb.ca')
        self.assertFalse(u.is_bulk)

    def test_bulk_user(self):
        u = User.extras.create_bulk_user(username='fred', email='fred@ewb.ca')
        self.assertTrue(u.is_bulk)
