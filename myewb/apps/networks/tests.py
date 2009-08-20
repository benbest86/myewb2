"""myEWB networks testing

This file is part of myEWB
Copyright 2009 Engineers Without Borders (Canada) Organisation and/or volunteer contributors

Last modified on 2009-07-29
@author Joshua Gorner
"""

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client
from django.core import mail

from base_groups.models import GroupMember
from base_groups.forms import GroupMemberForm
from networks.models import Network
from networks.forms import NetworkForm

class TestNetwork(TestCase):
    fixtures = ['test_networks.json']
    
    def setUp(self):
        # User one is a member and admin of network one (only)
        # User two is a member and non-admin of network two (only)
        self.user_one = User.objects.get(username="bob")
        self.user_two = User.objects.get(username="joe")
        
        self.network_one = Network.objects.get(slug="ewb-utoronto")
        self.network_two = Network.objects.get(slug="ewb-uwaterloo")
        
        self.member_one = GroupMember.objects.get(user=self.user_one, group=self.network_one)
        self.member_two = GroupMember.objects.get(user=self.user_two, group=self.network_two)
    
    def tearDown(self):
        pass
        
    def test_is_member(self):
        self.assertEquals(True, self.network_one.user_is_member(self.user_one))
        
    def test_is_not_member(self):
        self.assertEquals(False, self.network_one.user_is_member(self.user_two))
        
    def test_is_admin(self):
        self.assertEquals(True, self.member_one.is_admin)
        
    def test_is_not_admin(self):
        self.assertEquals(False, self.member_two.is_admin)    
    
    
class TestNetworkForm(TestCase):
    # fixtures = ['test_networks.json']
    
    def setUp(self):
        pass
    
    def tearDown(self):
        pass
        
    def test_valid_network(self):
        form = NetworkForm()
        data = {
            "slug": "ewb-carleton",
            "name": "Carleton University Chapter",
            "description": "Ottawa, ON",
            "network_type": "U",
            "private": "False"
        }
        form = NetworkForm(data)
        if not form.is_valid():
            for error in form.errors:
                print error
        self.assertEquals(True, form.is_valid())
        
        
    # Can't really think of a situation at this stage that would cause the form to be *invalid*...
    # unless of course a field is missing

class TestNetworkMail(TestCase):
    """
    Tests emailing of members in a network.
    """
    fixtures = ['test_networks.json']

    def setUp(self):
        self.ewb = Network.objects.get(slug='ewb')
        self.waterloo = Network.objects.get(slug='ewb-uwaterloo')

    def tearDown(self):
        pass

    def test_simple_email(self):
        body = 'Hi!\nAnd welcome!'
        subject = 'Welcome to the awesomeness of Django/Pinax powered MyEWB.'
        self.ewb.send_mail_to_members(subject, body)
        self.assertEquals(1, len(mail.outbox))
        msg = mail.outbox[0]
        self.assertEquals(msg.body, body)
        self.assertEquals(msg.subject, subject)
        self.assertEquals(msg.to, [u'list-ewb@ewb.ca'])
        self.assertEquals(msg.from_email, u'Engineers Without Borders <ewb@ewb.ca>')
        self.assertEquals(len(msg.bcc), len(self.ewb.get_member_emails()))

    def test_unviersity_network_mail(self):
        body = 'Hi!\nAnd welcome!'
        subject = 'Welcome to the awesomeness of Django/Pinax powered MyEWB.'
        self.waterloo.send_mail_to_members(subject, body)
        self.assertEquals(1, len(mail.outbox))
        msg = mail.outbox[0]
        self.assertEquals(msg.to, [u'list-ewb-uwaterloo@ewb.ca'])
        self.assertEquals(msg.from_email, u'University of Waterloo Chapter <ewb-uwaterloo@ewb.ca>')
        self.assertEquals(len(msg.bcc), len(self.waterloo.get_member_emails()))


class TestNetworkTopicMail(TestCase):
    """
    Tests emailing of new topics when specified.
    """
    fixtures = ['test_networks.json']

    def setUp(self):
        self.ewb = Network.objects.get(slug='ewb')
        self.logged_in = self.client.login(username='ben', password='passw0rd')

    def tearDown(self):
        self.client.logout()

    def test_new_topic_with_email(self):
        response = self.client.post('/networks/ewb/topics/', {'title': 'first post', 'body':'Lets make a new topic.', 'send_as_email': True, 'tags':'first, post'})
        self.assertEquals(response.status_code, 200)
        self.assertEquals(1, len(mail.outbox))
        self.assertEquals(len(self.ewb.get_member_emails()), len(mail.outbox[0].bcc))

    def test_new_topic_without_email(self):
        response = self.client.post('/networks/ewb/topics/', {'title': 'second post', 'body':'But no email this time', 'send_as_email': False, 'tags':'second, post'})
        self.assertEquals(0, len(mail.outbox))

