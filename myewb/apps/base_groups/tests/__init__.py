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
        status_record = GroupStatusRecord.objects.get(user=self.user, group=self.bg)
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

class TestAcceptedMembershipHistory(TestCase):
    """
    Tests to ensure that changing status on members creates
    the proper membership history.
    """
    def setUp(self):
        pass

    def tearDown(self):
        pass

class TestInvitedMembershipHistory(TestCase):
    """
    Tests to ensure that changing status on members creates
    the proper membership history.
    """
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_invite_member(self):
        pass

    def test_change_invited_to_accepted(self):
        pass

    def test_remove_invited_member(self):
        pass

class TestRequestedMembershipHistory(TestCase):
    """
    Tests to ensure that changing status on members creates
    the proper membership history.
    """
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_remove_requested_member(self):
        pass

    def test_accept_requested_member(self):
        pass

class TestAdminMembershipHistory(TestCase):
    """
    Tests to ensure that changing status on members creates
    the proper membership history.
    """
    def setUp(self):
        pass

    def tearDown(self):
        pass
