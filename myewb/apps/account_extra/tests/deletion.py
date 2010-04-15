from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
from emailconfirmation.models import EmailAddress
from base_groups.models import BaseGroup

class TestDeletion(TestCase):
    
    def setUp(self):
        pass
    
    def tearDown(self):
        pass
        
    def test_verified_cleanup(self):
        """
        Test the softdelete() method, which removes a user from all groups,
        removes personal information, and marks the account as inactive.
        
        But keeps the historical record.
        """
        user1 = User.objects.create(username="user1", email="email@ewb.ca")
        email2 = EmailAddress.objects.add_email(user=user1, email="email2@ewb.ca")
        
        user1.firstname = "First Name"
        user1.lastname = "Last Name"
        user1.save()

        creator = User.objects.create(username="groupcreator", email="groupcreator@ewb.ca")
        group = BaseGroup.objects.create(name="test", slug="test", creator=creator)
        group.add_member(user1)
        
        self.assertEquals(user1.firstname, 'First Name')
        self.assertEquals(user1.email, 'email@ewb.ca')
        self.assertTrue(group.user_is_member(user1))
        
        # delete the user!
        user1.softdelete()
        
        # and test
        self.assertEquals(user1.firstname, 'First Name')    # is this intended? not sure yet. but it makes posts look better!
        self.assertFalse(user1.is_active)
        self.assertEquals(user1.email, '')
        self.assertEquals(EmailAddress.objects.filter(user=user1).count(), 0)
        self.assertFalse(group.user_is_member(user1))

