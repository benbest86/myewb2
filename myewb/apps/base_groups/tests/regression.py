from django.test import TestCase
from django.contrib.auth.models import User, AnonymousUser

from base_groups.models import BaseGroup

class TestAddCreatorToGroup(TestCase):
    """
    A regression test for ticket #390
    (https://cotonou.ewb.ca/fastrac/myewb2/ticket/390)
    where group creators are not automatically added to the group.

    This test fails under r164.
    """

    def test_creator_added_to_group(self):
        u = User.objects.create_user('user', 'user@ewb.ca', 'password')
        bg = BaseGroup.objects.create(slug='bg', name='a base group', creator=u)
        self.assertTrue(bg.user_is_member(u), 'User should exists as a member of group it created.')
        # creator should also be an admin
        self.assertTrue(bg.user_is_admin(u), 'User should be an admin of the group it created.')

class TestAddBulkMemberToGroup(TestCase):
    """
    Related to ticket #392. Adding a method to BaseGroup to properly add new
    users to group depending on whether they are true users or bulk users.
    """

    def setUp(self):
        pass

    def tearDown(self):
        User.objects.all().delete()
        BaseGroup.objects.all().delete()

    def test_add_bulk_user_to_group(self):
        # create a bulk user with no password
        super_user = User.objects.create_superuser('super', 'root@ewb.ca', 'password')
        u = User.extras.create_bulk_user('bulk', 'email@e.com')
        group = BaseGroup.objects.create(slug='new-group', name='a random base group.', creator=super_user)
        group.add_member(u)
        new_member = group.members.get(user=u)
        self.assertTrue(new_member.is_bulk)

    def test_add_real_user_to_group(self):
        super_user = User.objects.create_superuser('super', 'root@ewb.ca', 'password')
        # create a real user with a password
        u = User.objects.create_user('bulk', 'email@e.com', 'password')
        group = BaseGroup.objects.create(slug='new-group', name='a random base group.', creator=super_user)
        group.add_member(u)
        new_member = group.members.get(user=u)
        self.assertTrue(new_member.is_accepted)
