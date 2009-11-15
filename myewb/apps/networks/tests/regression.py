from django.test import TestCase

from django.contrib.auth.models import User
from networks.models import Network

class TestAddCreatorToNetwork(TestCase):
    """
    Regression test for https://cotonou.ewb.ca/fastrac/myewb2/ticket/390.
    Network creator is not added to newtork as admin.
    """

    def test_add_creator_to_network(self):
        u = User.objects.create_user('creator', 'c@ewb.ca', 'password')
        net = Network.objects.create(slug='new-net', name='new-net', creator=u)
        self.assertTrue(net.user_is_member(u))
        self.assertTrue(net.user_is_admin(u))

