from django.test import TestCase

from django.contrib.auth.models import User, AnonymousUser

from base_groups.models import BaseGroup, GroupMember, GroupMemberRecord

class TestGroupMethods(TestCase):
    """
    Test the common methods of a BaseGroup
    """
    setup = False
    
    def setUp(self):
        # could use a fixture instead... but i like this better.  easier to edit.
        if not self.setup:
            # create group
            self.group_creator = User.objects.create_user('creator', 'c@ewb.ca')
            self.bg = BaseGroup.objects.create(slug='bg', name='generic base group', description='description1', creator=self.group_creator, model='Network')
            self.invisible = BaseGroup.objects.create(slug='bg2', name='generic invisible base group', description='description2', creator=self.group_creator, visibility='M')
            self.invisible_child = BaseGroup.objects.create(slug='bg3', name='generic invisible child group', description='description3', creator=self.group_creator, visibility='M')
            self.visible_child = BaseGroup.objects.create(slug='bg4', name='generic visible child group', description='description4', creator=self.group_creator, visibility='E')
            
            # add a group admin
            self.groupadmin = User.objects.create_user('groupadmin', 'groupadmin@ewb.ca')
            self.bg.add_member(self.groupadmin)
            self.invisible.add_member(self.groupadmin)
            gmember = GroupMember.objects.get(user=self.groupadmin, group=self.bg)
            gmember.is_admin = True
            gmember.save()          # should we create BaseGroup.add_admin()?? but that would require refactoring all the membership forms...
            self.invisible.add_member(self.groupadmin)
            gmember = GroupMember.objects.get(user=self.groupadmin, group=self.invisible)
            gmember.is_admin = True
            gmember.save()          # should we create BaseGroup.add_admin()?? but that would require refactoring all the membership forms...
            
            # add a normal group member
            self.member = User.objects.create_user('member', 'member@ewb.ca')
            self.bg.add_member(self.member)
            self.invisible.add_member(self.member)
            
            # and add a regular non-member user
            self.user = User.objects.create_user('user', 'user@ewb.ca')
            
            # and make someone a member of one group, but not the other 
            self.user2 = User.objects.create_user('user2', 'user2@ewb.ca')
            self.bg.add_member(self.user2)
            
            # and a site admin
            self.siteadmin = User.objects.create_user('siteadmin', 'siteadmin@ewb.ca')
            self.siteadmin.is_superuser = True
            self.siteadmin.save()
            
            
            self.setup = True

    def tearDown(self):
        pass

    def test_is_visible(self):
        # whoa. how many different places is this check implented in??!!!
        # really need to consolidate!
        # (one here, one in decorators, one in helpers...)
        
        # regular public group is visible to all
        self.assertTrue(self.bg.is_visible(self.siteadmin))
        self.assertTrue(self.bg.is_visible(self.group_creator))
        self.assertTrue(self.bg.is_visible(self.groupadmin))
        self.assertTrue(self.bg.is_visible(self.member))
        self.assertTrue(self.bg.is_visible(self.user))
        self.assertTrue(self.bg.is_visible(AnonymousUser()))

        # private group is only visible to members
        self.assertTrue(self.invisible.is_visible(self.siteadmin))
        self.assertTrue(self.invisible.is_visible(self.group_creator))
        self.assertTrue(self.invisible.is_visible(self.groupadmin))
        self.assertTrue(self.invisible.is_visible(self.member))
        self.assertFalse(self.invisible.is_visible(self.user))
        self.assertFalse(self.invisible.is_visible(AnonymousUser()))

        # private child is always visible to parent admins
        self.assertTrue(self.invisible_child.is_visible(self.siteadmin))
        self.assertTrue(self.invisible_child.is_visible(self.group_creator))
        self.assertTrue(self.invisible_child.is_visible(self.groupadmin))
        self.assertFalse(self.invisible_child.is_visible(self.member))
        self.assertFalse(self.invisible_child.is_visible(self.user))
        self.assertFalse(self.invisible_child.is_visible(AnonymousUser()))

    def test_user_is_member(self):
        self.assertTrue(self.bg.user_is_member(self.siteadmin, True))
        self.assertFalse(self.bg.user_is_member(self.siteadmin))
        self.assertTrue(self.bg.user_is_member(self.group_creator))
        self.assertTrue(self.bg.user_is_member(self.groupadmin))
        self.assertTrue(self.bg.user_is_member(self.member))
        self.assertFalse(self.bg.user_is_member(self.user))
        self.assertFalse(self.bg.user_is_member(AnonymousUser()))

    def test_get_member_emails(self):
        emails = set(self.invisible.get_member_emails())
        expected_emails = ('c@ewb.ca', 'groupadmin@ewb.ca', 'member@ewb.ca')
        
        self.assertEquals(emails, expected_emails)
        
    def test_add_member(self):
        # this is tested in setup... if this method is broken, plenty of other tests will fail!
        pass
    
    def test_add_email(self):
        self.bg.add_email('bulkemail@ewb.ca')
        
        user = User.objects.get(email='bulkemail@ewb.ca')
        self.assertTrue(user.is_bulk)
        self.assertTrue(self.bg.get_member_emails().count('bulkemail@ewb.ca'))

    def test_remove_member(self):
        self.bg.remove_member(self.user2)
        self.assertFalse(self.bg.user_is_member(self.user2))
        self.assertTrue(self.user2.is_active)   #user should not be deleted =)
        
    def test_get_visible_children(self):
        # admin can see all children
        print "testing site admin"
        self.assertEquals(self.bg.get_visible_children(self.siteadmin), (self.invisible_child, self.visible_child))
        print "testing creator"
        self.assertEquals(self.bg.get_visible_children(self.group_creator), (self.invisible_child, self.visible_child))
        print "testing group admin"
        self.assertEquals(self.bg.get_visible_children(self.groupadmin), (self.invisible_child, self.visible_child))
        
        # the rest can only see visible children
        self.assertEquals(self.bg.get_visible_children(self.member), (self.visible_child))
        self.assertEquals(self.bg.get_visible_children(self.user), (self.visible_child))
        self.assertEquals(self.bg.get_visible_children(AnonymousUser()), (self.visible_child))
        
    def test_get_accepted_member(self):
        self.bg.add_email('bulkemail2@ewb.ca')
        bulkuser = User.objects.get(email='bulkemail2@ewb.ca')
        
        self.assertTrue(list(self.bg.get_accepted_members()).count(self.group_creator))
        self.assertTrue(list(self.bg.get_accepted_members()).count(self.groupadmin))
        self.assertTrue(list(self.bg.get_accepted_members()).count(self.member))
        self.assertFalse(list(self.bg.get_accepted_members()).count(bulkuser))
        self.assertFalse(list(self.bg.get_accepted_members()).count(self.user))
        self.assertFalse(list(self.bg.get_accepted_members()).count(AnonymousUser()))

