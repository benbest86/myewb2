from django.test import TestCase
from django.contrib.auth.models import User, AnonymousUser

from base_groups.models import BaseGroup

class TestVisibility(TestCase):
    def setUp(self):
        self.u = User.objects.create_user('user', 'user@ewb.ca', 'password')
        self.u2 = User.objects.create_user('user2', 'user2@ewb.ca', 'password')
        self.u3 = User.objects.create_user('user3', 'user3@ewb.ca', 'password')
        
        self.anon = AnonymousUser()
        
        self.bg = BaseGroup.objects.create(slug='bg', name='a base group', creator=self.u)
        # no need to add u - should be a member by virtue of creating
        self.bg.add_member(self.u2)

    def test_public_group(self):
        """
        Test BaseGroup.is_visible for public groups
        """

        self.bg.visibility = 'E'

        self.assertTrue(self.bg.is_visible(self.anon), 'Guest should be able to see public group.')
        self.assertTrue(self.bg.is_visible(self.u), 'Creator should be able to see public group.')
        self.assertTrue(self.bg.is_visible(self.u2), 'Member should be able to see public group.')
        self.assertTrue(self.bg.is_visible(self.u3), 'Non-member should be able to see public group.')

    def test_private_group(self):
        """
        Test BaseGroup.is_visible for private groups
        """

        self.bg.visibility = 'M'

        self.assertFalse(self.bg.is_visible(self.anon), 'Guest should not be able to see private group.')
        self.assertTrue(self.bg.is_visible(self.u), 'Creator should be able to see private group.')
        self.assertTrue(self.bg.is_visible(self.u2), 'Member should be able to see private group.')
        self.assertFalse(self.bg.is_visible(self.u3), 'Non-member should not be able to see private group.')
