"""myEWB networks testing

This file is part of myEWB
Copyright 2009 Engineers Without Borders (Canada) Organisation and/or volunteer contributors

Last modified on 2009-07-29
@author Joshua Gorner
"""

from django.contrib.auth.models import User
from django.test import TestCase
from networks.models import Network
from networks.helpers import is_exec_over

class TestNetworkHelpers(TestCase):
    
    def setUp(self):
        # User one is an exec
        # User two is a member of the chapter
        # User three is not a member of the chapter
        # User four is an exec, but of a different chapter
        
        creator = User.objects.create(username="creator",
                                      first_name="creator",
                                      last_name="creator")

        self.network = Network.objects.create(slug="testgroup",
                                              name="test group",
                                              description="testing",
                                              creator=creator)
        self.network2 = Network.objects.create(slug="testgroup2",
                                               name="test group2",
                                               description="testing2",
                                               creator=creator)

        self.user_one = User.objects.create(username="userone",
                                            first_name="userone",
                                            last_name="userone",
                                            is_active=True,
                                            is_staff=False,
                                            is_superuser=False)
        self.user_two = User.objects.create(username="usertwo",
                                            first_name="usertwo",
                                            last_name="usertwo",
                                            is_active=True,
                                            is_staff=False,
                                            is_superuser=False)
        self.user_three = User.objects.create(username="userthree",
                                              first_name="userthree",
                                              last_name="userthree",
                                              is_active=True,
                                              is_staff=False,
                                              is_superuser=False)
        self.user_four = User.objects.create(username="userfour",
                                             first_name="userfour",
                                             last_name="userfour",
                                             is_active=True,
                                             is_staff=False,
                                             is_superuser=False)
        
        m1 = self.network.add_member(self.user_one)
        m1.is_admin = True
        m1.save()
        m2 = self.network.add_member(self.user_two)
        #m3 = not member
        m4 = self.network.add_member(self.user_four)

        m5 = self.network2.add_member(self.user_four)
        m5.is_admin = True
        m5.save()
        m6 = self.network2.add_member(self.user_three)
        
    def tearDown(self):
        pass
        
    def test_is_exec_over(self):
        self.assertEquals(True, is_exec_over(self.user_one, self.user_one))
        self.assertEquals(True, is_exec_over(self.user_two, self.user_one))
        self.assertEquals(False, is_exec_over(self.user_three, self.user_one))
        self.assertEquals(True, is_exec_over(self.user_four, self.user_one))
        
        self.assertEquals(False, is_exec_over(self.user_one, self.user_four))
        self.assertEquals(False, is_exec_over(self.user_two, self.user_four))
        self.assertEquals(True, is_exec_over(self.user_three, self.user_four))
        self.assertEquals(True, is_exec_over(self.user_four, self.user_four))
