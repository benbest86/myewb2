from regression import *

class TestUserDuckPunches(TestCase):
    """
    Testing additions to the User class.
    """

    def test_non_bulk_user(self):
        u = User.objects.create_user(username='fred', email='fred@ewb.ca')
        self.assertFalse(u.is_bulk)

    def test_bulk_user(self):
        u = User.extras.create_bulk_user(username='fred', email='fred@ewb.ca')
        self.assertTrue(u.is_bulk)
