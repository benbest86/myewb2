# coding: utf-8

"""myEWB testing

This file is part of myEWB
Copyright 2009 Engineers Without Borders (Canada) Organisation and/or volunteer contributors

Last modified: 2009-07-21
@author: Joshua Gorner
"""

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client

from profiles.forms import ProfileForm, StudentRecordForm
from profiles.models import MemberProfile, StudentRecord

class TestMemberProfile(TestCase):
    fixtures = ['test_member_profiles.json']
    
    def setUp(self):
        pass
    
    def tearDown(self):
        pass
        
    def test_friend_contact_info(self):
        """ensure that users 2 and 3 can "see" each others' contact info"""
        c = Client()
        c.post("/account/login/", {'username': 'joe', 'password': 'passw0rd'})
        response = c.get("/profiles/john/")
        self.assertContains(response, "Toronto, ON")
        
        d = Client()
        d.post("/account/login/", {'username': 'john', 'password': 'passw0rd'})
        response = d.get("/profiles/joe/")
        self.assertContains(response, "Berlin")
        
    def test_staff_contact_info(self):
        """ensure that user 1 (staff member) can see contact info of non-friend user 2"""
        c = Client()
        c.post("/account/login/", {'username': 'bob', 'password': 'passw0rd'})
        response = c.get("/profiles/joe/")
        self.assertContains(response, "Berlin")
        
    def test_stranger_contact_info(self):
        """TODO: ensure that user 2 (not staff member) cannot see contact info of non-friend user 1"""
        c = Client()
        c.post("/account/login/", {'username': 'joe', 'password': 'passw0rd'})
        response = c.get("/profiles/bob/")
        self.assertNotContains(response, "366 Adelaide")

class TestMemberProfileForm(TestCase):
    fixtures = ['test_member_profiles.json']
    
    def setUp(self):
        self.user_one = User.objects.get(username='bob')
        self.profile_one = MemberProfile.objects.get(user=self.user_one)
        self.student_one = StudentRecord.objects.get(user=self.user_one)
        
        self.user_two = User.objects.get(username='joe')
        self.profile_two = MemberProfile.objects.get(user=self.user_two)
        
        self.user_three = User.objects.get(username='john')
        self.profile_three = MemberProfile.objects.get(user=self.user_three)
        
        self.user_four = User.objects.get(username='jane')
        self.profile_four = MemberProfile.objects.get(user=self.user_four)
    
    def tearDown(self):
        pass
        
    def test_valid_profile(self):
        form = ProfileForm(instance=self.profile_one)
        # include a bad country to force an error
        data = {
            "name": "John Smith",
            "about": "John likes wine",
            "location": "Paris",
            "website": "http://python.org",
            "street_address": "80, bd Auguste-Blanqui",
            "street_address_two": "Cedex 13",
            "city": "Paris",
            "postal_code": "75707",
            "country": "FR",
            "date_of_birth": "1986-05-05",
        }
        form = ProfileForm(data)
        self.assertEquals(True, form.is_valid())
        
    def test_bad_url(self):        
        form = ProfileForm(instance=self.profile_one)
        # include a bad url to force an error
        data = {
            "name": "John Smith",
            "about": "John likes wine",
            "location": "France maybe!",
            "website": "httpasd://python.org"            
        }
        form = ProfileForm(data)
        self.assertEquals(False, form.is_valid())

    def test_bad_country(self):
        form = ProfileForm(instance=self.profile_one)
        # include a bad country to force an error
        data = {
            "name": "John Smith",
            "about": "John likes wine",
            "location": "Paris",
            "website": "http://python.org",
            "street_address": "80, bd Auguste-Blanqui",
            "street_address_two": "Cedex 13",
            "city": "Paris",
            "postal_code": "75707",
            "country": "FA",    # wrong: France is "FR", there is no "FA"
        }
        form = ProfileForm(data)
        self.assertEquals(False, form.is_valid())

    def test_bad_date_of_birth(self):
        form = ProfileForm(instance=self.profile_one)
        # include a bad country to force an error
        data = {
            "name": "John Smith",
            "about": "John likes wine",
            "location": "Paris",
            "website": "http://python.org",
            "street_address": "80, bd Auguste-Blanqui",
            "street_address_two": "Cedex 13",
            "city": "Paris",
            "postal_code": "75707",
            "country": "FR",
            "date_of_birth": "19860505",
        }
        form = ProfileForm(data)
        self.assertEquals(False, form.is_valid())
        
    def test_alternate_bad_date_of_birth(self):
        form = ProfileForm(instance=self.profile_one)
        # include a bad country to force an error
        data = {
            "name": "John Smith",
            "about": "John likes wine",
            "location": "Paris",
            "website": "http://python.org",
            "street_address": "80, bd Auguste-Blanqui",
            "street_address_two": "Cedex 13",
            "city": "Paris",
            "postal_code": "75707",
            "country": "FR",
            "date_of_birth": "05-05-1986",
        }
        form = ProfileForm(data)
        self.assertEquals(False, form.is_valid())
        
    def test_is_not_student_outside_dates(self):
        # initial record: "bob" has one student record, with grad date 2009-04-30
        self.assertEquals(False, self.profile_one.student())
        
    def test_is_student_open_ended(self):
        # "john" has a student record with start date before today but no grad date
        self.assertEquals(True, self.profile_three.student())
    
    def test_is_student_no_dates(self):
        # "jane" has a student record with no dates indicated
        self.assertEquals(True, self.profile_four.student())
