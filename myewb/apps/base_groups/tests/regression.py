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
