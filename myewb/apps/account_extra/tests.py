from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User

class TestAccountExtra(TestCase):
    fixtures = ['test_account_extra.json']
    
    def setUp(self):
        pass
    
    def tearDown(self):
        pass
        
    def test_signup(self):
        """ensure that user can signup using email address, but is not immediately logged in""" 
        prev_count = User.objects.all().count()
        c = Client()
        response = c.post("/account/signup/", {'email': 'testuser@ewb.ca', 'password1': 'passw0rd', 'password2': 'passw0rd'})
        new_count = User.objects.all().count()
        self.assertEqual(new_count, prev_count + 1)
        
        self.assertContains(response, "Verify your e-mail address")
        u = User.objects.latest('date_joined')
        self.assertFalse(u.message_set.filter(user=u, message__icontains="Successfully logged in").count() > 0)
        
    def test_username_fail(self):
        """ensure that user cannot set own username"""
        c = Client()
        response = c.post("/account/signup/", {'username': 'testuser', 'password1': 'passw0rd', 'password2': 'passw0rd'})
        self.assertTrue(User.objects.filter(email="testuser@ewb.ca").count() == 0)
        self.assertContains(response, "This field is required.")
        
    def test_duplicate_fail(self):
        """ensure that an email address cannot be used by more than one user"""
        c = Client()
        response = c.post("/account/signup/", {'email': 'bob@roberts.com', 'password1': 'passw0rd', 'password2': 'passw0rd'})
        self.assertTrue(User.objects.filter(email="bob@roberts.com").count() == 1)
        self.assertContains(response, "This email address has already been used. Please use another.")
        
    def test_username_login(self):
        """verify that we support login using legacy usernames"""
        c = Client()
        response = c.post("/account/login/", {'login_name': 'bob', 'password': 'passw0rd'})
        u = User.objects.get(username="bob")
        self.assertTrue(u.message_set.filter(user=u, message__icontains="Successfully logged in").count() > 0)
        
    def test_verified_primary_email_login(self):
        """verify that we support login using verified, primary email address"""
        c = Client()
        response = c.post("/account/login/", {'login_name': 'bob@roberts.com', 'password': 'passw0rd'})
        u = User.objects.get(username="bob")
        self.assertTrue(u.message_set.filter(user=u, message__icontains="Successfully logged in").count() > 0)
        
    def test_verified_secondary_email_login(self):
        """verify that we support login using verified, non-primary email address"""
        c = Client()
        response = c.post("/account/login/", {'login_name': 'bob.roberts@gmail.com', 'password': 'passw0rd'})
        u = User.objects.get(username="bob")
        self.assertTrue(u.message_set.filter(user=u, message__icontains="Successfully logged in").count() > 0)
        
    def test_unverified_primary_email_login(self):
        """verify that we do not support login using non-verified, primary email address"""
        c = Client()
        response = c.post("/account/login/", {'login_name': 'joe@smith.com', 'password': 'passw0rd'})
        u = User.objects.get(username="joe")
        self.assertFalse(u.message_set.filter(user=u, message__icontains="Successfully logged in").count() > 0)
        
    def test_unverified_secondary_email_login(self):
        """verify that we do not support login using non-verified, non-primary email address"""
        c = Client()
        response = c.post("/account/login/", {'login_name': 'joe.smith@gmail.com', 'password': 'passw0rd'})
        u = User.objects.get(username="joe")
        self.assertFalse(u.message_set.filter(user=u, message__icontains="Successfully logged in").count() > 0)
        
    def test_unused_email_failure(self):
        """verify that we do not login a user not in the system"""
        c = Client()
        response = c.post("/account/login/", {'login_name': 'blahblah@gmail.com', 'password': 'passw0rd'})
        self.assertContains(response, "The login credentials you specified are not correct.")