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

from networks.models import Network, NetworkMember
from networks.forms import NetworkForm, NetworkMemberForm

class TestNetwork(TestCase):
    fixtures = ['test_networks.json']
    
    def setUp(self):
        # User one is a member and admin of network one (only)
        # User two is a member and non-admin of network two (only)
        self.user_one = User.objects.get(username="bob")
        self.user_two = User.objects.get(username="joe")
        
        self.network_one = Network.objects.get(slug="ewb-utoronto")
        self.network_two = Network.objects.get(slug="ewb-uwaterloo")
        
        self.member_one = NetworkMember.objects.get(user=self.user_one, group=self.network_one)
        self.member_two = NetworkMember.objects.get(user=self.user_two, group=self.network_two)
    
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
