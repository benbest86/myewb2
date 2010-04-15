from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
from emailconfirmation.models import EmailAddress, EmailConfirmation

class TestAccountEmails(TestCase):
    
    def setUp(self):
        pass
    
    def tearDown(self):
        pass
        
    def test_verified_cleanup(self):
        """
        When an email address is verified, any unverified instances of the 
        same email address should be deleted.  If this results in a user with 
        no email addresses, then the user should be deleted too.
        """
        user1 = User.objects.create(username="user1")
        email1 = EmailAddress.objects.add_email(user=user1, email="email1@ewb.ca")
        email1.verified = True
        email1.save()
        # verify email1 so this account isn't auto-deleted later...
        
        email2 = EmailAddress.objects.add_email(user=user1, email="email2@ewb.ca")
        # email2 is unverified.
        
        # now add email2 to another account
        user2 = User.objects.create(username="user2")
        email2b = EmailAddress.objects.add_email(user=user2, email="email2@ewb.ca")
        
        # and add email2 to a third account
        user3 = User.objects.create(username="user3")
        email2c = EmailAddress.objects.add_email(user=user3, email="email2@ewb.ca")
        
        # email should be unverified on all accounts
        self.assertEquals(EmailAddress.objects.filter(user=user1, email="email2@ewb.ca").count(), 1)
        self.assertEquals(EmailAddress.objects.filter(user=user2, email="email2@ewb.ca").count(), 1)
        self.assertEquals(EmailAddress.objects.filter(user=user3, email="email2@ewb.ca").count(), 1)
        
        # verify email now on 2nd account
        email2b.verified = True
        email2b.save()
        
        # no longer on first account, but still in second
        self.assertEquals(EmailAddress.objects.filter(user=user1, email="email2@ewb.ca").count(), 0)
        self.assertEquals(EmailAddress.objects.filter(user=user2, email="email2@ewb.ca").count(), 1)

        # and third account should be deleted
        self.assertEquals(User.objects.filter(username="user3").count(), 0)

    def test_bulk_creation(self):
        """
        Test the User.extras.create_bulk_user() method
        """
        # simple test
        user = User.extras.create_bulk_user(email="blah@ewb.ca")
        self.assertNotEqual(user, None)
        self.assertTrue(user.is_bulk)
        self.assertEquals(user.email, "blah@ewb.ca")
        self.assertEquals(EmailAddress.objects.filter(user=user, email='blah@ewb.ca').count(), 1)
        
        # and, if the email is already in the system, return that user instead of creating a new one 
        email = EmailAddress.objects.get(user=user, email='blah@ewb.ca')
        email.verified = True
        email.save()
        
        user2 = User.extras.create_bulk_user("blah@ewb.ca")
        self.assertEquals(user, user2)
        
    def test_email_list(self):
        """
        Checks that the view showing a user's emails is accurate
        """
        user = User.objects.create_user(username="username", email="email@ewb.ca", password="password")
        EmailAddress.objects.add_email(user=user, email="email@ewb.ca")
        c = Client()
        c.login(username="username", password="password")
        response = c.get("/account/email/")
        self.assertContains(response, "email@ewb.ca")
        self.assertContains(response, "unverified")
        
        # now  verify the email
        email = EmailAddress.objects.get(email="email@ewb.ca")
        confirmation = EmailConfirmation.objects.get(email_address=email)
        EmailConfirmation.objects.confirm_email(confirmation.confirmation_key)
        
        response = c.get("/account/email/")
        self.assertContains(response, "email@ewb.ca")
        self.assertContains(response, "verified")
        self.assertNotContains(response, "unverified")

        # add another email.  it should show up and not be verified.
        response = c.post("/account/email/",
                          {'email': "email2@ewb.ca",
                           'action': "add"},
                          follow=True)
        self.assertContains(response, "email2@ewb.ca")
        self.assertContains(response, "unverified")
        
        # and test deletion too
        c.post("/account/email/",
               {'email': "email2@ewb.ca",
                'action': "remove"})
        response = c.get("/account/email/")     # need to re-get, since email2@ewb.ca will be in the user messages right after removal
        self.assertNotContains(response, "email2@ewb.ca")
        self.assertNotContains(response, "unverified")
        self.assertContains(response, "email@ewb.ca")
