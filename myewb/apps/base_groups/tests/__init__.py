from django.test import TestCase

from django.contrib.auth.models import User

from base_groups.models import BaseGroup, GroupMember, GroupStatusRecord
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
        GroupStatusRecord.objects.all().delete()
        GroupMember.objects.all().delete()
        BaseGroup.objects.all().delete()
        User.objects.all().delete()


class TestBulkMembershipHistory(TestMembershipHistory):
    """
    Tests to ensure that changing status on members creates
    the proper membership history.
    """
    def test_add_bulk_member(self):
        gm = GroupMember.objects.create(user=self.user, group=self.bg, request_status='B')
        status_record = GroupStatusRecord.objects.get(user=self.user, group=self.bg)
        self.assertEquals(status_record.status, 'recipient')
        # assert True and False for start and end since we can't predict the time of 
        # creation
        self.assertTrue(status_record.start)
        self.assertFalse(status_record.end)

    def test_remove_bulk_member(self):
        gm = GroupMember.objects.create(user=self.user, group=self.bg, request_status='B')
        gm.delete()
        # .get() here will ensure only a single record
        status_record = GroupStatusRecord.objects.get(user=self.user, group=self.bg)
        # assert an end has been given to our status_record
        self.assertTrue(status_record.end)

    def test_change_bulk_to_accepted(self):
        gm = GroupMember.objects.create(user=self.user, group=self.bg, request_status='B')
        gm.request_status = 'A'
        gm.save()
        status_records = GroupStatusRecord.objects.filter(user=self.user, group=self.bg)
        recipient_record = status_records.get(status='recipient')
        regular_record = status_records.get(status='regular')
        self.assertTrue(recipient_record.end)
        self.assertTrue(regular_record.start)
        self.assertFalse(regular_record.end)

class TestAcceptedMembershipHistory(TestMembershipHistory):
    """
    Tests to ensure that changing status on members creates
    the proper membership history.
    """

    def test_add_accepted_member(self):
        gm = GroupMember.objects.create(user=self.user, group=self.bg, request_status='A')
        status_record = GroupStatusRecord.objects.get(user=self.user, group=self.bg)
        self.assertEquals(status_record.status, 'regular')
        # assert True and False for start and end since we can't predict the time of 
        # creation
        self.assertTrue(status_record.start)
        self.assertFalse(status_record.end)

    def test_delete_accepted_member(self):
        gm = GroupMember.objects.create(user=self.user, group=self.bg, request_status='A')
        gm.delete()
        status_record = GroupStatusRecord.objects.get(user=self.user, group=self.bg)
        self.assertEquals(status_record.status, 'regular')
        # assert True and False for start and end since we can't predict the time of 
        # creation
        self.assertTrue(status_record.start)
        self.assertTrue(status_record.end)


class TestInvitedMembershipHistory(TestMembershipHistory):
    """
    Tests to ensure that changing status on members creates
    the proper membership history.
    """
    def test_invite_member(self):
        gm = GroupMember.objects.create(user=self.user, group=self.bg, request_status='I')
        status_record = GroupStatusRecord.objects.filter(user=self.user, group=self.bg)
        # no status record should be created for an invited user
        self.assertFalse(status_record.count())

    def test_change_invited_to_accepted(self):
        gm = GroupMember.objects.create(user=self.user, group=self.bg, request_status='I')
        gm.request_status = 'A'
        gm.save()
        status_record = GroupStatusRecord.objects.get(user=self.user, group=self.bg)
        self.assertEquals(status_record.status, 'regular')
        # assert True and False for start and end since we can't predict the time of 
        # creation
        self.assertTrue(status_record.start)
        self.assertFalse(status_record.end)

    def test_remove_invited_member(self):
        gm = GroupMember.objects.create(user=self.user, group=self.bg, request_status='I')
        gm.delete()
        status_record = GroupStatusRecord.objects.filter(user=self.user, group=self.bg)
        # no status record should be created for an invited user
        self.assertFalse(status_record.count())

class TestRequestedMembershipHistory(TestMembershipHistory):
    """
    Tests to ensure that changing status on members creates
    the proper membership history.
    """
    def test_add_request_member(self):
        gm = GroupMember.objects.create(user=self.user, group=self.bg, request_status='R')
        status_record = GroupStatusRecord.objects.filter(user=self.user, group=self.bg)
        # no status record should be created for an invited user
        self.assertFalse(status_record.count())

    def test_delete_requested_member(self):
        gm = GroupMember.objects.create(user=self.user, group=self.bg, request_status='R')
        gm.delete()
        status_record = GroupStatusRecord.objects.filter(user=self.user, group=self.bg)
        # no status record should be created for an invited user
        self.assertFalse(status_record.count())

    def test_accept_requested_member(self):
        gm = GroupMember.objects.create(user=self.user, group=self.bg, request_status='R')
        gm.request_status = 'A'
        gm.save()
        status_record = GroupStatusRecord.objects.get(user=self.user, group=self.bg)
        self.assertEquals(status_record.status, 'regular')
        # assert True and False for start and end since we can't predict the time of 
        # creation
        self.assertTrue(status_record.start)
        self.assertFalse(status_record.end)

class TestAdminMembershipHistory(TestCase):
    """
    Tests to ensure that changing status on members creates
    the proper membership history.
    """
    def setUp(self):
        pass

    def tearDown(self):
        pass
