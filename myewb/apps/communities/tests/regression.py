from django.test import TestCase

from django.contrib.auth.models import User
from communities.models import Community

class TestAddCreatorToCommunity(TestCase):
    """
    Regression test for https://cotonou.ewb.ca/fastrac/myewb2/ticket/390.
    Community creator is not added to newtork as admin.
    """

    def test_add_creator_to_network(self):
        u = User.objects.create_user('creator', 'c@ewb.ca', 'password')
        com = Community.objects.create(slug='new-com', name='new-com', creator=u)
        self.assertTrue(com.user_is_member(u))
        self.assertTrue(com.user_is_admin(u))

