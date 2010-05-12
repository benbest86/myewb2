import MySQLdb

from datetime import date, datetime
from django.core.management.base import NoArgsCommand
from siteutils import countries

from django.contrib.auth.models import User
from profiles.models import MemberProfile, StudentRecord, WorkRecord
from siteutils.models import Address, PhoneNumber
from champ.views import fix_encoding

from django.core.management.base import NoArgsCommand

from base_groups.models import BaseGroup, LogisticalGroup, GroupMemberRecord, GroupMember
from communities.models import Community, NationalRepList, ExecList
from networks.models import Network, ChapterInfo

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

        db2 = MySQLdb.connect(user='root',
                             passwd='',
                             db='myewb2-migration',
                             charset="utf8")
        c2 = db2.cursor()

        print "==============="
        print "Migrating users"
        print datetime.now()
        print "==============="
        print ""
        #self.migrate_users(c)
        
        print ""
        print "finished users at", datetime.now()
        print ""
        print ""
        
        print "==============="
        print "Migrating groups"
        print datetime.now()
        print "==============="
        print ""
        #self.migrate_groups(c, c2)
        
        print ""
        print "finished groups at", datetime.now()
        print ""
        print ""
        
        print "==============="
        print "Migrating tags"
        print datetime.now()
        print "==============="
        print ""
        #self.migrate_tags(c, c2)
        
        print ""
        print "finished tags at", datetime.now()
        print ""
        print ""
        
        print "==============="
        print "Migrating posts"
        print datetime.now()
        print "==============="
        print ""
        self.migrate_posts(c, c2)
        
        print ""
        print "finished posts at", datetime.now()
        print ""
        print ""
        
    
        
    def migrate_users(self, c):
        # ./manage.py reset --noinput account auth profiles siteutils ; ./manage.py migrate | tee users.log
        
        User.objects.create(id=1, username="admin", email="admin@ewb.ca")
        
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
            if row[20]:
                mp.gender = row[20].upper()
            if row[6]:
                mp.language = row[6][0].upper()
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
                mp.addresses.add(a)
                mp.save()
            
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

    def migrate_groups(self, c, c2):
        # ./manage.py reset --noinput base_groups communities networks ; ./manage.py migrate | tee groups.log
        
        # get all chapters first
        c.execute("SELECT * FROM groupchapter")
        chapterinfo = {}
        execlists = []
        for row in c.fetchall():
            chapterinfo[row[0]] = {'id': row[0],
                                   'address': row[1],
                                   'address1': row[2],
                                   'suite': row[3],
                                   'address2': row[4],
                                   'city': row[5],
                                   'province': row[6],
                                   'postalcode': row[7],
                                   'phone': row[9],
                                   'fax': row[10],
                                   'execId': row[11],
                                   'francophone': row[12],
                                   'professional': row[13]}
            execlists.append(row[11])
        
        c.execute("SELECT * FROM groups")
        counter = 0
        for row in c.fetchall():
            # causes problems. and doesn't exist anyway.
            if row[0] == 35:
                continue
            
            if counter % 100 == 0:
                try:
                    print "Groups: id", row[0], "- name", unicode(row[1]).encode("utf8"), "- slug", row[10]
                except:
                    print "meh. couldn't print", row[0]
                
            # what kind of group do we need?
            if row[7]:
                type = Network
            elif row[8]:
                type = ExecList
            elif row[13] and row[13] != '0':
                type = NationalRepList
            elif row[0] == 5 or row[0] == 593 or row[0] == 254:        # all-exec lists
                type = ExecList
            elif row[5]:
                type = LogisticalGroup
            else:
                type = Community
            
            # prepare data
            if row[4]:
                visibility = 'E'
                invite_only = False
            else:
                visibility = 'M'
                invite_only = True
            if row[12] is None:
                slug = row[10]
            else:
                slug = row[0]
                
            # basic group object
            grp = type.objects.create(id=row[0],
                                      slug=slug,
                                      name=row[1],
                                      creator_id=1,
                                      created=datetime.now(),
                                      description=row[2],
                                      visibility=visibility,
                                      invite_only=invite_only,
                                      is_active = row[6] | row[5],
                                      is_project=row[9],
                                      welcome_email=row[14]
                                      )

            # create chapter-specific info
            if type == Network:
                if chapterinfo[row[0]]['professional']:
                    grp.network_type = 'R'
                else:
                    grp.network_type = 'U'
                grp.save
                
                addr2 = ""
                if chapterinfo[row[0]]['suite']:
                    addr2 += "Apt " + chapterinfo[row[0]]['suite'] + "|n"
                if chapterinfo[row[0]]['address2']:
                    addr2 += chapterinfo[row[0]]['address2']
                ch = ChapterInfo.objects.create(network=grp,
                                                chapter_name=row[1],
                                                street_address=chapterinfo[row[0]]['address1'],
                                                street_address_two=addr2,
                                                city=chapterinfo[row[0]]['city'],
                                                province=chapterinfo[row[0]]['province'],
                                                postal_code=chapterinfo[row[0]]['postalcode'],
                                                phone=chapterinfo[row[0]]['phone'],
                                                fax=chapterinfo[row[0]]['fax'],
                                                francophone=chapterinfo[row[0]]['francophone'],
                                                student= not chapterinfo[row[0]]['professional']
                                               )
                
        # assign parent groups separately, since using a parent that comes later
        # in the dump will cause an error
        # also do slugs here, since the slug may rely on the parent's name
        c.execute("SELECT * FROM groups")
        for row in c.fetchall():
            if row[12]:
                 grp = BaseGroup.objects.get(id=row[0])
                 parent = BaseGroup.objects.get(id=row[12])
                 grp.parent = parent
                 grp.slug = parent.slug + "-" + row[10]
                 while BaseGroup.objects.filter(slug=grp.slug).count() > 0:
                     grp.slug = grp.slug + "a"
                 grp.from_email = grp.slug + "@my.ewb.ca"
                 grp.save()
                 try:
                     print "Re-parenting", row[0], unicode(row[1]).encode("utf8"), grp.slug
                 except:
                     print "meh, couldn't print", row[0]

        # and build memberships
        #c.execute("SELECT * FROM roles WHERE userid=152")
        c.execute("SELECT * FROM roles")
        for row in c.fetchall():
            # excluded users...
            if row[5] == 1 or row[5] == 2:
                continue
            
            print "Role", row[0], ": user", row[5], "group", row[6], "level", row[4], "start", row[1], "end", row[2]
            
            start = row[1]
            end = row[2]
            title = row[3]
            level = row[4]      # r m s l
            #user = User.objects.get(pk=row[5])
            #group = BaseGroup.objects.get(pk=row[6])
            
            # special case: this is the main EWB group, so deals with account creation
            if row[5] == 1:
                user.date_joined = start
                if end is not None:
                    user.is_active = False
                user.save()
            else:
                # find admin level
                if level == 'l':
                    is_admin = True
                else:
                    is_admin = False
                    
                # role is ended.. create the  snapshots
                if end is not None:
                    """
                    GroupMemberRecord.objects.create(group=group,
                                                     user=user,
                                                     datetime=start,
                                                     membership_start=True,
                                                     is_admin=is_admin,
                                                     admin_title=title,
                                                     joined=start,
                                                     imported=True)
                    GroupMemberRecord.objects.create(group=group,
                                                     user=user,
                                                     datetime=end,
                                                     membership_end=True,
                                                     joined=start,
                                                     imported=True)
                    """
                    c2.execute("""INSERT INTO base_groups_groupmemberrecord  
                                    SET is_admin=%d, 
                                        admin_title=%s, 
                                        joined=%s, 
                                        group_id=%d,  
                                        user_id=%d, 
                                        datetime=%s, 
                                        membership_start=%d, 
                                        membership_end=%d,
                                        imported=%d""",
                                        (is_admin, title, start, row[6], row[5],
                                         start, True, False, True))
                    c2.execute("""INSERT INTO base_groups_groupmemberrecord  
                                    SET is_admin=%d,
                                        joined=%s, 
                                        group_id=%d,  
                                        user_id=%d, 
                                        datetime=%s, 
                                        membership_start=%d, 
                                        membership_end=%d,
                                        imported=%d""",
                                        (is_admin, start, row[6], row[5],
                                         end, False, True, True))
                else:
                    # create or update the role
                    # (in myEWB1, admins had a second role - in myEWB 2, they
                    #  will only have one role)
                    # and no need to do snapshot creation, the signals will do that for us
                    """ 
                    gm, created = GroupMember.objects.get_or_create(group=group,
                                                                    user=user,
                                                                    joined=start,
                                                                    imported=True)
                    gm.is_admin=is_admin
                    gm.admin_title=title
                    if created:
                        gm.joined=start
                    gm.save()
                    """
                    c2.execute("""SELECT id FROM base_groups_groupmember
                                    WHERE group_id=%d AND user_id=%d""",
                                    (row[6], row[5]))
                    id = c2.fetchone()
                    if id:
                        c2.execute("""UPDATE base_groups_groupmember
                                        SET is_admin=%d,
                                            admin_title=%s
                                        WHERE id=%d""", 
                                            (is_admin, title, id[0]))
                        c2.execute("""INSERT INTO base_groups_groupmemberrecord  
                                        SET is_admin=%d,
                                            joined=%s, 
                                            group_id=%d,  
                                            user_id=%d, 
                                            datetime=%s, 
                                            membership_start=%d, 
                                            membership_end=%d,
                                            imported=%d""",
                                            (is_admin, start, row[6], row[5],
                                             start, False, False, True))
                    else:
                        c2.execute("""INSERT INTO base_groups_groupmember
                                        SET is_admin=%d,
                                            admin_title=%s,
                                            joined=%s,
                                            imported=%d,
                                            group_id=%d,    
                                            user_id=%d""", 
                                            (is_admin, title, start, True, row[6], row[5]))
                        c2.execute("""INSERT INTO base_groups_groupmemberrecord  
                                        SET is_admin=%d,
                                            joined=%s, 
                                            group_id=%d,  
                                            user_id=%d, 
                                            datetime=%s, 
                                            membership_start=%d, 
                                            membership_end=%d,
                                            imported=%d""",
                                            (is_admin, start, row[6], row[5],
                                             start, True, False, True))


    def migrate_tags(self, c, c2):
        # ./manage.py reset --noinput tagging tag_threadedcomments mythreadedcomments ; ./manage.py migrate | tee tags.log
        
        # get all tags
        c.execute("SELECT * FROM tags")
        for row in c.fetchall():
            print "tag", row[0], "-", row[2] 
            # see if this tag already exists
            c2.execute("""SELECT id FROM tagging_tag WHERE name=%s""",
                       row[2])
            oldid = c2.fetchone()

            # doesn't exist? insert it
            if not oldid:
                c2.execute("""INSERT INTO tagging_tag
                            SET id=%s, name=%s""",
                                (row[0], row[2]))
                
            # this is an actual tag
            if row[1] == row[2]:
                # if a tag with this name already existed, update it to match the IDs.
                if oldid:
                    c2.execute("""UPDATE tagging_tag
                                SET id=%s
                                WHERE id=%s""",
                                    (row[0], oldid[0]))
                    c2.execute("""UPDATE tag_app_tagalias
                                SET tag_id=%s
                                WHERE tag_id=%s""",
                                    (row[0], oldid[0]))
                    
            # this is just an alias
            else:
                if not oldid:
                    oldid = [row[0]]
                c2.execute("""INSERT INTO tag_app_tagalias
                            SET id=%s, tag_id=%s, alias=%s""",
                            (row[0], oldid[0], row[1]))

    def migrate_posts(self, c, c2):
        # ./manage.py reset --noinput topics group_topics threadedcomments mythreadedcomments ; ./manage.py migrate | tee posts.log
        
        # get the base_group content type
        c2.execute("""SELECT id FROM django_content_type WHERE name='base group'
                        AND app_label='base_groups' AND model='basegroup'""")
        row = c2.fetchone()
        bgtype = row[0]
        
        # get all posts 
        c.execute("SELECT * FROM posts")
        for row in c.fetchall():
            print "post", row[0], "date", row[4], "parent", row[5], "group", row[7], "subject", row[1]
            
            # do some data cleanup
            title = row[1]
            if len(title) > 50:
                title = title[0:49]
                
            # check for invalid posts
            if not row[6] or not row[7]:
                continue
            
            # is a post
            if not row[5]:
                c2.execute("""INSERT INTO topics_topic
                            SET id=%s,
                                content_type_id=%s,
                                object_id=%s,
                                title=%s,
                                creator_id=%s,
                                created=%s,
                                modified=%s,
                                body=%s,
                                tags=%s""",
                            (row[0], bgtype, row[7], title, row[6], row[4], row[4], row[3], ""))
                c2.execute("""INSERT INTO group_topics_grouptopic
                            SET topic_ptr_id=%s,
                                parent_group_id=%s,
                                send_as_email=%s,
                                last_reply=%s,
                                score=0, score_modifier=0""",
                                (row[0], row[7], row[9], row[12]))
                
            # is a reply
            else:
                pass