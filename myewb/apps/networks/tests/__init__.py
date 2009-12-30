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

from emailconfirmation.models import EmailAddress
from base_groups.models import GroupMember
from base_groups.forms import GroupMemberForm
from networks.models import Network
from networks.forms import NetworkForm
from siteutils.helpers import get_email_user

# import regression tests
from regression import *

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
        response = self.client.post('/networks/ewb/posts/', {'title': 'first post', 'body':'Lets make a new topic.', 'send_as_email': True, 'tags':'first, post', 'attach_count':0,})
        self.assertEquals(response.status_code, 302)
        self.assertEquals(1, len(mail.outbox))
        self.assertEquals(len(self.ewb.get_member_emails()), len(mail.outbox[0].bcc))

    def test_new_topic_without_email(self):
        response = self.client.post('/networks/ewb/topics/', {'title': 'second post', 'body':'But no email this time', 'send_as_email': False, 'tags':'second, post'})
        self.assertEquals(0, len(mail.outbox))

class TestBulkMembers(TestCase):
    """
    Tests for functionality associated with bulk email users.
    """
    fixtures = ['test_networks.json']

    def setUp(self):
        self.joe = User.objects.get(username='joe')
        self.superman = User.objects.get(username='superman')
        self.ewb = Network.objects.get(slug='ewb')

    def tearDown(self):
        self.ewb.members.all().delete()
        try:
            self.client.logout()
        except:
            pass
        User.objects.all().delete()

    def test_create_bulk_user(self):
        self.assertTrue(self.client.login(username='superman', password='passw0rd'))
        self.client.post('/networks/ewb/bulk/', {'emails':'test@server.com'})
        bulk_users = self.ewb.members.bulk()
        # we should have one bulk user at this point
        self.assertEquals(bulk_users.count(), 1)
        bulk_user = bulk_users[0]
        # bulk user should have our input address
        self.assertEquals(bulk_user.user.email, 'test@server.com')
        # bulk user should not show up in a list of accepted members
        self.assertFalse(bulk_user in self.ewb.get_accepted_members())

        self.ewb.send_mail_to_members('Test', 'Mail')
        msg = mail.outbox[0]
        # bulk user should get an email
        self.assertTrue('test@server.com' in msg.bcc)

    def test_create_bulk_users(self):
        email_list = '''one@one.com
        two@two.com
        three@three.com
        four@four.com
        '''
        self.client.login(username='superman', password='passw0rd')
        self.client.post('/networks/ewb/bulk/', {'emails':email_list})
        self.assertEquals(self.ewb.members.bulk().count(), 4)
        for email in email_list.split():
            self.assertTrue(get_email_user(email).member_groups.get(group__slug='ewb'))

    def test_invalid_bulk_emails(self):
        invalid_email_list = '''@one.com
        two@two
        three@t?hree.com
        four@four.c
        '''
        self.client.login(username='superman', password='passw0rd')
        response = self.client.post('/networks/ewb/bulk/', {'emails':invalid_email_list})
        for email in invalid_email_list:
            self.assertTrue(response.content.find('%s is not a valid email.' % email))



    def test_new_member_without_verification(self):
        """
        New members shouldn't inherit membership until they confirm
        their email address.
        """
        new_network = Network.objects.create(slug='new-net', name='new network', creator=self.superman)
        self.assertTrue(self.client.login(username='superman', password='passw0rd'))
        self.client.post('/networks/new-net/bulk/', {'emails':'test3@server.com'})

        self.client.logout()
        new_user_info = {
                # 'username': 'jeff',
                'password1': 'test',
                'password2': 'test',
                'email': 'test3@server.com',
                }
        self.client.post('/account/signup/', new_user_info)
        self.assertEquals(new_network.members.bulk().count(), 1)
        bulk_user = new_network.members.bulk().get().user
        self.assertEquals(bulk_user.email, 'test3@server.com')
        # only original bulk email member should have email
        self.assertEquals(User.objects.filter(email='test3@server.com').count(), 1)
        self.assertEquals(User.objects.filter(email='test3@server.com').get(), bulk_user)
            

    def test_verify_email_for_bulk_user(self):
        new_network = Network.objects.create(slug='new-net', name='new network', creator=self.superman)
        self.assertTrue(self.client.login(username='superman', password='passw0rd'))
        self.client.post('/networks/new-net/bulk/', {'emails':'test2@server.com'})
        bulk_user = get_email_user('test2@server.com')
        self.joe.emailaddress_set.add(EmailAddress(email='test2@server.com'))
        email_address = self.joe.emailaddress_set.get(email='test2@server.com')
        email_address.verified = True
        email_address.save()
        joe_member = new_network.members.get(user=self.joe)
        # joe should be accepted
        self.assertTrue(joe_member.is_accepted)
        # old dummy user should be gone
        self.assertRaises(User.DoesNotExist, User.objects.get, id=bulk_user.id)
        self.assertEquals(new_network.members.bulk().count(), 0)
        new_network.delete()
        
    def test_verify_unsubscribe(self):
        email = '''one@one.com'''
        self.client.login(username='superman', password='passw0rd')
        self.client.post('/networks/ewb/bulk/', {'emails':email})
        self.assertEquals(self.ewb.members.filter(user__email=email).count(), 1)
        self.client.logout()
        
        self.client.post('/unsubscribe/', {'email':email})
        
        self.assertRaises(GroupMember.DoesNotExist, self.ewb.members.get, user__email=email)



class TestCustomGroupMemberManager(TestCase):
    """
    Tests the custom methods added to the GroupMember manager.
    """
    fixtures = ['test_networks.json']

    def setUp(self):
        self.joe = User.objects.get(username='joe')
        self.superman = User.objects.get(username='superman')
        self.ewb = Network.objects.get(slug='ewb')
        self.new_network = Network.objects.create(slug='new-net', name='new network', creator=self.superman)

    def tearDown(self):
        self.ewb.members.all().delete()
        try:
            self.client.logout()
        except:
            pass
        User.objects.all().delete()

    def test_accepted_members(self):
        self.client.login(username='superman', password='passw0rd')
        self.assertFalse(self.joe in [member.user for member in self.new_network.members.accepted()])
        self.client.post('/networks/new-net/bulk/', {'emails':'joe@smith.com'})
        self.assertTrue(self.joe in [member.user for member in self.new_network.members.accepted()])

    def test_bulk_members(self):
        self.client.login(username='superman', password='passw0rd')
        self.assertFalse('bulk@test.ca' in [member.user.email for member in self.new_network.members.bulk()])
        self.client.post('/networks/new-net/bulk/', {'emails':'bulk@test.ca'})
        self.assertTrue('bulk@test.ca' in [member.user.email for member in self.new_network.members.bulk()])

