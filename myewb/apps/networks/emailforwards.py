"""myEWB email forwards for chapters

This file is part of myEWB
Copyright 2009 Engineers Without Borders (Canada) Organisation and/or volunteer contributors
Some code derived from Pinax, copyright 2008-2009 James Tauber and Pinax Team, licensed under the MIT License

Last modified on 2009-08-17
@author Francis Kung
"""

from django import forms
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _
from emailconfirmation.models import EmailAddress

from base_groups.models import BaseGroup
from base_groups.forms import BaseGroupForm, GroupMemberForm
import ldap
from ldap import modlist as ml
import settings
        
objectClass = ['top','ewbMailForward','ewbPerson']
basedn = 'ou=testing,dc=ewb,dc=ca'
scope = ldap.SCOPE_ONELEVEL
aliasField = 'ewbMailAddress'
recipientField = 'ewbMailInbox'
myewbIdField = 'ewbMyewbID'

def connect():
    try:
        l = ldap.initialize(settings.LDAP_HOST)
        l.bind_s(settings.LDAP_BIND_DN, settings.LDAP_BIND_PW)
    except:
        return None
    return l

def findForwards(user):
    """
    Find all forwards for a given user.
    Takes a user object and returns a list of addresses
    """
    
    l = connect()
    
    if l:
        filter = "(&"
        for o in objectClass:
            filter += "(objectClass=%s)" % o
        filter += "(%s=%s))" % (myewbIdField, user.id);
    
        forwards = []
        result = l.search_s(basedn, scope, filter, [aliasField])
        for dn, entry in result:
            for addr in entry[aliasField]:
                forwards.append(addr)
    
        return forwards
    
    else:
        return []

def findUser(forward):
    """
    Find a user, given the forward (returns None if does not exist)
    """
    
    l = connect()
    
    if l:
        filter = "(&"
        for o in objectClass:
            filter += "(objectClass=%s)" % o
        filter += "(%s=%s))" % (aliasField, str(forward));
    
        forwards = []
        result = l.search_s(basedn, scope, filter, [myewbIdField])
        try:
            for dn, entry in result:
                for id in entry[myewbIdField]:
                    user = User.objects.get(id=id)
                    return user
        except:
            pass
    
    return None
    

def addAddress(user, address):
    """
    Adds a forward to a given user
    """
    
    l= connect()
    
    if l:
        # check that address is not already taken
        olduser = findUser(address)
    
        if olduser:
            return False
    
        # create user if needed
        filter = "(&"
        for o in objectClass:
            filter += "(objectClass=%s)" % o
        filter += "(%s=%s))" % (myewbIdField, user.id);
        result = l.search_s(basedn, scope, filter)

        if len(result) == 0:
            attrs = {}
            attrs[myewbIdField] = "%s" % user.id
            attrs[recipientField] = "%s" % str(user.email)
            attrs['cn'] = "%s %s" % (user, user.email)
            attrs['cn'] = "%s" % (user)
            attrs['objectClass'] = objectClass
            attrs[aliasField] = "%s" % str(address)
        
            modlist = ml.addModlist(attrs)
        
            name = "%s=%s,%s" % (myewbIdField, user.id, basedn)
            result = l.add_s(name, modlist)
    
        else:
            dn, attrs = result[0]
            result = l.modify_s(dn, [(ldap.MOD_ADD,
                                      aliasField,
                                      str(address))])
    
        return result
    
    else:
        return False

def removeAddress(user, address):
    l = connect()
    
    if l:
        oldaddresses = findForwards(user)
    
        if address not in oldaddresses:
            return False
    
        oldaddresses.remove(address)
    
        # remove user if needed
        name = "%s=%s,%s" % (myewbIdField, user.id, basedn)
        if len(oldaddresses) == 0:
            result = l.delete_s(name)
        
        else:
            result = l.modify_s(name, [(ldap.MOD_DELETE,
                                        aliasField,
                                        str(address))])
        
        return result
    
    else:
        return False

def updateUser(user, address):
    l = connect()
    
    if l:
        if len(findForwards(user)) > 0:
            name = "%s=%s,%s" % (myewbIdField, user.id, basedn)
            result = l.modify_s(name, [(ldap.MOD_REPLACE,
                                        recipientField,
                                        str(address))])
        else:
            result = True
        
        return result
    
    else:
        return False

def forwardsForGroup(slug):
    l = connect()
    
    if l:
        filter = "(&"
        for o in objectClass:
            filter += "(objectClass=%s)" % o
        filter += "(%s=*@%s.ewb.ca))" % (aliasField, slug);
    
        forwards = []
        result = l.search_s(basedn, scope, filter, [aliasField, myewbIdField])
        for dn, entry in result:
            for addr in entry[aliasField]:
                user = User.objects.get(id=entry[myewbIdField][0])
                forwards.append({aliasField:user})
    
        return forwards

    else:
        return []

    
def set_primary_email(sender, instance=None, **kwargs):
    """
    Automatically sets a verified email to primary if no verified address exists yet.
    Also updates LDAP for email forwards if the primary email is changed.
    """
    if instance is not None and instance.verified:
        user = instance.user
        if instance.primary == False:
            # if we only have one email it is this one
            if user.emailaddress_set.count() == 1:
                instance.set_as_primary()
                updateUser(user, instance.email)
        else:
            updateUser(user, instance.email)

post_save.connect(set_primary_email, sender=EmailAddress)
