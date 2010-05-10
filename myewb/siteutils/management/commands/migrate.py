import MySQLdb

from datetime import date, datetime
from django.core.management.base import NoArgsCommand
from siteutils import countries

from django.contrib.auth.models import User
from profiles.models import MemberProfile, StudentRecord, WorkRecord
from siteutils.models import Address, PhoneNumber

from django.core.management.base import NoArgsCommand

class Command(NoArgsCommand):
    help = "Migrates data from myEWB1"
    requires_model_validation = False

    def handle_noargs(self, **options):
        print "Starting migration"
        db = MySQLdb.connect(user='root',
                             passwd='',
                             db='myewbdeploy',
                             charset="utf8")
        c = db.cursor()

        print "==============="
        print "Migrating users"
        print datetime.now()
        print "==============="
        print ""
        self.migrate_users(c)
        
        print ""
        print "finished users at", datetime.now()
        print ""
        print ""
        
        
    def migrate_users(self, c):
        c.execute("SELECT * FROM users")
        counter = 0
        for row in c.fetchall():
            if row[0] == 1 or row[0] == 2:
                continue       # skip the guest user
            
            if counter % 100 == 0:
                print "Users: id %d - name %s - email %s" % (row[0], row[1], row[5])
                
            # clean up username
            is_bulk = False
            username = row[1]
            if not username:
                username = User.objects.make_random_password()
                while User.objects.filter(username=username).count() > 0:   # ensure uniqueness
                    username = User.objects.make_random_password()
                is_bulk = True
                
            # email cannot be null, so make it blank if needed
            email = row[5]
            if email == None:
                email = ""
                
            # basic user object
            u = User.objects.create(id=row[0],
                                    username=username,
                                    password=row[2],
                                    first_name=row[3],
                                    last_name=row[4],
                                    email=email,
                                    is_bulk=is_bulk)
            if row[25]:
                u.last_login = row[25]
                u.save()
                
            # build member profile info
            mp = u.get_profile()
            mp.first_name = row[3]
            mp.last_name = row[4]
            mp.gender = row[20]
            if row[6]:
                mp.language = row[6][0]
            if row[21]:
                mp.date_of_birth = date(row[21], 1, 1)
            mp.membership_expiry = row[24]
            mp.current_login = row[25]
            mp.previous_login = row[26]
            mp.login_count = row[27]
            mp.adminovision = row[28]
            mp.about = row[43]
            mp.show_emails = row[47]
            mp.show_replies = row[48]
            mp.address_updated = row[45]
            mp.replies_as_emails = row[47]
            mp.replies_as_emails2 = row[47]
            mp.watchlist_as_emails = row[47]
            mp.grandfathered = True
            mp.save()
        
            # add phone numbers
            if row[15]:
                p = PhoneNumber.objects.create(label='Home',
                                               number=row[15],
                                               content_object=mp)
                p.save()
            if row[16]:
                p = PhoneNumber.objects.create(label='Home Fax',
                                               number=row[16],
                                               content_object=mp)
                p.save()
            if row[17]:
                p = PhoneNumber.objects.create(label='Work',
                                               number=row[17],
                                               content_object=mp)
                p.save()
            if row[18]:
                p = PhoneNumber.objects.create(label='Mobile',
                                               number=row[18],
                                               content_object=mp)
                p.save()
            if row[19]:
                p = PhoneNumber.objects.create(label='Other',
                                               number=row[19],
                                               content_object=mp)
                p.save()
        
            # set address if provided
            if row[23] == "y" and row[8] and row[11] and row[12] and row[13] and row[14]:
                street = row[8].strip()
                if row[9].strip():
                    street = street + "\nApt " + row[9].strip()
                if row[10].strip():
                    street = street + "\n" + row[10].strip()
                a = Address.objects.create(label='Address',
                                           street=street,
                                           city=row[11].strip(),
                                           province=row[12].strip()[0:2],   # TODO: do a better pycountry lookup?
                                           postal_code=row[13].strip(),
                                           country=row[14].strip(),
                                           content_object=mp)
            
            # student records
            if row[29] or row[30] or row[31] or row[32] or row[33] or row[34]:
                sr = StudentRecord()
                sr.user = u
                sr.institution = row[30]
                sr.student_number = row[29]
                sr.field = row[31]
                if row[32] == 1:
                    sr.level = 'HS'
                elif row[32] == 2:
                    sr.level = 'UG'
                elif row[32] == 3:
                    sr.level = 'GR'
                elif row[32] == 4:
                    sr.level = 'OT'
                if row[34] and row[33]:
                    sr.graduation_date = date(row[34], row[33], 1)
                sr.save()
                
            # work records
            if row[35] or row[36] or row[37] or row[38] or row[39]:
                wr = WorkRecord()
                wr.user = u
                wr.employer = row[35]
                wr.sector = row[36]
                wr.position = row[37]
                if row[38] == 1:
                    wr.company_size = 'tiny'
                elif row[38] == 2:
                    wr.company_size = 'small'
                elif row[38] == 3:
                    wr.company_size = 'medium'
                elif row[38] == 4:
                    wr.company_size = 'large'
                    
                if row[39] == 1:
                    wr.income_level = 'low'
                elif row[39] == 2:
                    wr.income_level = 'lower_mid'
                elif row[39] == 3:
                    wr.income_level = 'upper_mid'
                elif row[39] == 4:
                    wr.income_level = 'high'
                
                wr.save()
