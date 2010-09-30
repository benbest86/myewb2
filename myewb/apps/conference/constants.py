from django.utils.translation import ugettext_lazy as _
import settings

FOOD_CHOICES = (('none', _("no special preferences")),
                ('vegetarian', _("vegetarian")),
                ('vegan', _("vegan"))
    )

# this should be a dictionary, but needs to be a tuple to be used as an ENUM
CONF_CODES = (('a', "test"),
              ('b', "unifar"),
              ('c', "unimid"),
              ('d', "uniclose"),
              ('e', "staff")
             )
              
CONF_HASH = settings.CONF_HASH
    
CONF_OPTIONS = {'confreg-2011-double-test': {'cost': 175,
                                            'name': "Test - shared bed"},
                'confreg-2011-single-test': {'cost': 305,
                                            'name': "Test - single bed"},
                'confreg-2011-nohotel-test': {'cost': 140,
                                            'name': "Test - no room"},

                'confreg-2011-double-open': {'cost': 620,
                                               'name': "Open registration (unsubsidized) - shared bed"},
                'confreg-2011-single-open': {'cost': 740,
                                               'name': "Open registration (unsubsidized) - single bed"},
                'confreg-2011-nohotel-open': {'cost': 500,
                                               'name': "Open registration (unsubsidized) - no room"},

                'confreg-2011-double-unifar': {'cost': 100,
                                               'name': "University chapter (BC/AB/NF) - shared bed"},
                'confreg-2011-single-unifar': {'cost': 220,
                                               'name': "University chapter (BC/AB/NF) - single bed"},
                'confreg-2011-nohotel-unifar': {'cost': 80,
                                               'name': "University chapter (BC/AB/NF) - no room"},

                'confreg-2011-double-unimid': {'cost': 200,
                                               'name': "University chapter (SK/MB/NB/NS) - shared bed"},
                'confreg-2011-single-unimid': {'cost': 320,
                                               'name': "University chapter (SK/MB/NB/NS) - single bed"},
                'confreg-2011-nohotel-unimid': {'cost': 160,
                                               'name': "University chapter (SK/MB/NB/NS) - no room"},

                'confreg-2011-double-uniclose': {'cost': 350,
                                               'name': "University chapter (ON/QB) - shared bed"},
                'confreg-2011-single-uniclose': {'cost': 470,
                                               'name': "University chapter (ON/QB) - single bed"},
                'confreg-2011-nohotel-uniclose': {'cost': 280,
                                               'name': "University chapter (ON/QB) - no room"},

                'confreg-2011-double-staff': {'cost': 0,
                                             'name': "EWB Staff - quad room"},
                'confreg-2011-single-staff': {'cost': 0,
                                             'name': "EWB Staff - double room"},
                'confreg-2011-nohotel-staff': {'cost': 0,
                                             'name': "EWB Staff - no room"}
               }

ROOM_CHOICES = (('nohotel', _('Conference only (no hotel)')),
                ('double', _('double registration (shared bed)')),
                ('single', _('single registration (own bed)'))
               ) 
                

PASTEVENTS = (('1', '1'),
              ('2', '2'),
              ('3', '3'),
              ('4', '4'),
              ('5', '5'),
              ('6', '6'),
              ('7', '7'),
              ('8', '8'),
              ('9', '9'),
              ('10', '10'),
              )

OVRANK = (('1', '1'))