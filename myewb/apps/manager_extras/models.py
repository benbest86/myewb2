from django.db import models
from django.contrib.auth.models import User, UserManager

# Create your models here.

class ExtraUserManager(UserManager):
    """
    An empty subclass of Manager that other
    modules can add methods to in order to 
    customize manager behaviour.
    """
    pass

User.add_to_class('extras', ExtraUserManager())
