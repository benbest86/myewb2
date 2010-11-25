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
              ('e', "staff"),
              ('f', "cityfar"),
              ('g', "citymid"),
              ('h', "cityclose"),
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

                'confreg-2011-friday-open': {'cost': 120,
                                               'name': "Friday attendance"},
                'confreg-2011-saturday-open': {'cost': 120,
                                               'name': "Saturday attendance"},
                'confreg-2011-twoday-open': {'cost': 220,
                                               'name': "Friday/Saturday attendance"},
                'confreg-2011-fridaystudent-open': {'cost': 60,
                                               'name': "Friday attendance (student)"},
                'confreg-2011-saturdaystudent-open': {'cost': 60,
                                               'name': "Saturday attendance (student)"},
                'confreg-2011-twodaystudent-open': {'cost': 110,
                                               'name': "Friday/Saturday attendance (student)"},

                'confreg-2011-friday-discounted': {'cost': 100,
                                               'name': "Friday attendance (discounted)"},
                'confreg-2011-saturday-discounted': {'cost': 100,
                                               'name': "Saturday attendance (discounted)"},
                'confreg-2011-twoday-discounted': {'cost': 180,
                                               'name': "Friday/Saturday attendance (discounted)"},
                'confreg-2011-fridaystudent-discounted': {'cost': 60,
                                               'name': "Friday attendance (student)"},
                'confreg-2011-saturdaystudent-discounted': {'cost': 60,
                                               'name': "Saturday attendance (student)"},
                'confreg-2011-twodaystudent-discounted': {'cost': 110,
                                               'name': "Friday/Saturday attendance (student)"},

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

                'confreg-2011-double-cityfar': {'cost': 250,
                                               'name': "City network (BC/AB/NF) - shared bed"},
                'confreg-2011-single-cityfar': {'cost': 370,
                                               'name': "City network (BC/AB/NF) - single bed"},
                'confreg-2011-nohotel-cityfar': {'cost': 200,
                                               'name': "City network (BC/AB/NF) - no room"},

                'confreg-2011-double-citymid': {'cost': 350,
                                               'name': "City network (SK/MB/NB/NS) - shared bed"},
                'confreg-2011-single-citymid': {'cost': 470,
                                               'name': "City network (SK/MB/NB/NS) - single bed"},
                'confreg-2011-nohotel-citymid': {'cost': 280,
                                               'name': "City network (SK/MB/NB/NS) - no room"},

                'confreg-2011-double-cityclose': {'cost': 500,
                                               'name': "City network (ON/QB) - shared bed"},
                'confreg-2011-single-cityclose': {'cost': 620,
                                               'name': "City network (ON/QB) - single bed"},
                'confreg-2011-nohotel-cityclose': {'cost': 400,
                                               'name': "City network (ON/QB) - no room"},

                'confreg-2011-double-staff': {'cost': 0,
                                             'name': "EWB Staff - quad room"},
                'confreg-2011-single-staff': {'cost': 0,
                                             'name': "EWB Staff - double room"},
                'confreg-2011-nohotel-staff': {'cost': 0,
                                             'name': "EWB Staff - no room"},

                'confreg-2011-double-alumni': {'cost': 125,
                                             'name': "EWB Alumni"},
                'confreg-2011-single-alumni': {'cost': 125,
                                             'name': "EWB Alumni"},
                'confreg-2011-nohotel-alumni': {'cost': 125,
                                             'name': "EWB Alumni"}
               
               }

ROOM_CHOICES = (('nohotel', _('Conference only (no hotel)')),
                ('double', _('double registration (shared bed)')),
                ('single', _('single registration (own bed)'))
               ) 
                
EXTERNAL_CHOICES = (('fridaystudent', _('Friday attendance (student)')),
                    ('saturdaystudent', _('Saturday attendance (student)')),
                    ('twodaystudent', _('Friday and Saturday attendance (student)')),
                    ('friday', _('Friday attendance')),
                    ('saturday', _('Saturday attendance')),
                    ('twoday', _('Friday and Saturday attendance'))
                   ) 
                

PASTEVENTS = (('0', '0'),
              ('1', '1'),
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

AFRICA_FUND = (('75', 'Yes - $75'),
               ('45', 'Yes - $45'),
               ('20', 'Yes - $20'),
               ('', 'No thank you'))

EXTERNAL_GROUPS = (('NGO member', 'NGO member'),
                   ('Engineering professional', 'Engineering professional'),
                   ('University student', 'University student'),
                   ('High school student', 'High school student'),
                   ('University professor / academia', 'University professor / academia'),
                   ('Government', 'Government'),
                   ('Other', 'Other'))
