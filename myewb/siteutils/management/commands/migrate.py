import MySQLdb
import re

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
        #self.migrate_user_emails(c, c2)
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
        #self.migrate_posts(c, c2)
        
        print ""
        print "finished posts at", datetime.now()
        print ""
        print ""
        
        print "==============="
        print "Migrating events"
        print datetime.now()
        print "==============="
        print ""
        #self.migrate_events(c, c2)
        
        print ""
        print "finished events at", datetime.now()
        print ""
        print ""
        
        print "==============="
        print "Migrating whiteboards"
        print datetime.now()
        print "==============="
        print ""
        #self.migrate_whiteboards(c, c2)
        
        print ""
        print "finished whiteboards at", datetime.now()
        print ""
        print ""
        
        print "==============="
        print "Migrating CHAMP"
        print datetime.now()
        print "==============="
        print ""
        #self.migrate_champ(c, c2)
        
        print ""
        print "finished CHAMP at", datetime.now()
        print ""
        print ""
        
        print "==============="
        print "Migrating stats"
        print datetime.now()
        print "==============="
        print ""
        self.migrate_stats(c, c2)
        
        print ""
        print "finished stats at", datetime.now()
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

    def migrate_user_emails(self, c, c2):
        # ./manage.py reset --noinput emailconfirmation ; ./manage.py migrate | tee useremails.log

        c.execute("SELECT * FROM useremails")
        for row in c.fetchall():
            print "email address", row[1], "for", row[0]
            c2.execute("""INSERT INTO emailconfirmation_emailaddress
                        SET user_id=%s,
                            email=%s,
                            `primary`=0,
                            verified=1""",
                            (row[0], row[1]))
            
        print "setting primary addresses"
        c2.execute("""UPDATE emailconfirmation_emailaddress e, auth_user u
                    SET e.`primary`=1
                    WHERE e.user_id=u.id AND e.email=u.email""")
            
        
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
            if row[7] or row[0] == 3:
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
            if row[0] == 1:
                slug = "ewb"
            elif row[0] == 3:
                slug = "natloffice"
            elif row[12] is None:
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
            elif row[5] == 3:
                is_admin = True
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
        
        # get various content types
        c2.execute("""SELECT id FROM django_content_type WHERE name='base group'
                        AND app_label='base_groups' AND model='basegroup'""")
        row = c2.fetchone()
        bgtype = row[0]
        
        c2.execute("""SELECT id FROM django_content_type
                        WHERE app_label='group_topics' AND model='grouptopic'""")
        row = c2.fetchone()
        gttype = row[0]
        
        # get all posts 
        c.execute("SELECT * FROM posts")
        for row in c.fetchall():
            try:
                print "post", row[0], "date", row[4], "parent", row[5], "group", row[7], "subject", row[1]
            except:
                print "eh, can't print", row[0]
            
            # do some data cleanup
            title = row[1]
            if len(title) > 50:
                title = title[0:49]
                
            # check for invalid posts
            if not row[6] or not row[7]:
                continue
            
            # is a post
            if not row[5]:
                # stitch intro & body together
                fullbody = ""
                if row[2]:
                    fullbody = row[2]
                    if fullbody[:-3] == "...":
                        fullbody = fullbody[0:-3]
                    else:
                        fullbody = fullbody + "\n\n"
                if row[3]:
                    if row[3][0:3] == "...":
                        fullbody = fullbody + row[3][3:]
                    else:
                        fullbody = fullbody + row[3] 
                        
                # create the post
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
                            (row[0], bgtype, row[7], title, row[6], row[4], row[4], fullbody, ""))
                c2.execute("""INSERT INTO group_topics_grouptopic
                            SET topic_ptr_id=%s,
                                parent_group_id=%s,
                                send_as_email=%s,
                                last_reply=%s,
                                score=0, score_modifier=0,
                                converted=0""",
                                (row[0], row[7], row[9], row[12]))
                
            # is a reply
            else:
                c2.execute("""INSERT INTO threadedcomments_threadedcomment
                            SET id=%s,
                                content_type_id=%s,
                                object_id=%s,
                                user_id=%s,
                                date_submitted=%s,
                                date_modified=%s,
                                comment=%s,
                                is_public=1,
                                is_approved=0,
                                converted=0""",
                                (row[0], gttype, row[5], row[6], row[4], row[4], row[3]))

        # do all post tags 
        c.execute("SELECT * FROM tags2posts")
        for row in c.fetchall():
            c2.execute("""SELECT id FROM tagging_taggeditem
                        WHERE tag_id=%s AND content_type_id=%s AND object_id=%s""",
                        (row[1], gttype, row[0]))
            thetag = c2.fetchone()
            if not thetag:
                print "post", row[0], "tag", row[1], " - inserting"
                c2.execute("""INSERT INTO tagging_taggeditem
                            SET tag_id=%s,
                                content_type_id=%s,
                                object_id=%s""",
                                (row[1], gttype, row[0]))
                c2.execute("""SELECT name FROM tagging_tag WHERE id=%s""",
                           (row[1]))
                tagname = c2.fetchone()
                if tagname is None:
                    tagname = [""]
                c2.execute("""UPDATE topics_topic
                            SET tags=CONCAT(CONCAT(tags, ","), %s)
                            WHERE id=%s""",
                            (tagname[0], row[0]))
            else:
                print "post", row[0], "tag", row[1], " - found as", thetag[0]

        # this is a Good Idea.
        c2.execute("ALTER TABLE  `group_topics_grouptopic` ADD INDEX (  `last_reply` )")
        c2.execute("ALTER TABLE  `threadedcomments_threadedcomment` ADD INDEX (  `object_id` )")
        c2.execute("ALTER TABLE  `threadedcomments_threadedcomment` ADD INDEX (  `date_submitted` )")
        c2.execute("ALTER TABLE  `threadedcomments_threadedcomment` ADD INDEX (  `is_public` ,  `is_approved` ) ;")
        c2.execute("ALTER TABLE  `topics_topic` ADD INDEX (  `object_id` )")
        c2.execute("ALTER TABLE  `topics_topic` ADD INDEX (  `created` )")
        
        # watchlists too
        c.execute("SELECT * FROM flaggedposts")
        for row in c.fetchall():
            c2.execute("""SELECT id FROM group_topics_watchlist
                        WHERE owner_id=%s""",
                        (row[1]))
            listid = c2.fetchone()
            if not listid:
                c2.execute("""INSERT INTO group_topics_watchlist
                            SET name='watchlist',
                                owner_id=%s""",
                                (row[1]))
                c2.execute("SELECT LAST_INSERT_ID()")
                listid = c2.fetchone()
                print "watchlist - post", row[0], "to user", row[1], "(creating", listid[0], ")"
            else:
                print "watchlist - post", row[0], "to user", row[1], "(found", listid[0], ")"
                
            c2.execute("""INSERT INTO group_topics_watchlist_posts
                        SET watchlist_id=%s,
                            grouptopic_id=%s""",
                            (listid[0], row[0]))
                
    def migrate_events(self, c, c2):
        # ./manage.py reset --noinput events ; ./manage.py migrate | tee events.log

        # get various content types
        c2.execute("""SELECT id FROM django_content_type
                    WHERE app_label='communities' AND model='community'""")
        row = c2.fetchone()
        cmtype = row[0]
        
        c2.execute("""SELECT id FROM django_content_type
                        WHERE app_label='networks' AND model='network'""")
        row = c2.fetchone()
        nttype = row[0]
        
        c2.execute("""SELECT id FROM django_content_type
                        WHERE app_label='base_groups' AND model='logisticalgroup'""")
        row = c2.fetchone()
        lgtype = row[0]
        
        # get all events
        c.execute("SELECT * FROM events")
        for row in c.fetchall():
            c2.execute("""SELECT model FROM base_groups_basegroup WHERE id=%s""",
                       (row[4]))
            model = c2.fetchone()
            
            if model[0] == "Network":
                ctype = nttype
            elif model[0] == "LogisticalGroup":
                ctype = lgtype
            else:
                ctype = cmtype
            
            c2.execute("""INSERT INTO events_event
                        SET id=%s,
                        title=%s,
                        description=%s,
                        slug=%s,
                        location=%s,
                        postal_code='',
                        start=%s,
                        end=%s,
                        owner_id=1,
                        content_type_id=%s,
                        object_id=%s,
                        parent_group_id=%s,
                        converted=0""",
                        (row[0], row[1], row[3], "event%d"%row[0], row[2],
                         row[5], row[6], ctype, row[4], row[4]))
            try:
                print "event", row[0], "-", row[1], ", attached to", ctype
            except:
                print "meh, couldn't print for", row[0] 


    def migrate_whiteboards(self, c, c2):
        # ./manage.py reset --noinput whiteboard ; ./manage.py migrate | tee whiteboards.log

        # get various content types
        c2.execute("""SELECT id FROM django_content_type WHERE name='base group'
                        AND app_label='base_groups' AND model='basegroup'""")
        row = c2.fetchone()
        bgtype = row[0]
        
        c2.execute("""SELECT id FROM django_content_type
                        WHERE app_label='group_topics' AND model='grouptopic'""")
        row = c2.fetchone()
        gttype = row[0]

        c2.execute("""SELECT id FROM django_content_type
                        WHERE app_label='events' AND model='event'""")
        row = c2.fetchone()
        evtype = row[0]

        # get all whiteboards
        c.execute("SELECT * FROM whiteboard WHERE enabled=1")
        for row in c.fetchall():
            # skip empty whiteboards
            if not row[1] or row[0] == 91:
                continue
            
            if row[6]:
                ctype = evtype
                oid = row[6]
                title = "Event%d" % row[6]
                
                c2.execute("""UPDATE events_event
                            SET whiteboard_id=%s
                            WHERE id=%s""",
                            (row[0], row[6]))
                 
            elif row[7]:
                ctype = gttype
                oid = row[7]
                title = "Post%d" % row[7]

                c2.execute("""UPDATE group_topics_grouptopic
                            SET whiteboard_id=%s
                            WHERE topic_ptr_id=%s""",
                            (row[0], row[7]))
                 
            elif row[8]:
                ctype = bgtype
                oid = row[8]
                title = "Whiteboard"
                
                c2.execute("""UPDATE base_groups_basegroup
                            SET whiteboard_id=%s
                            WHERE id=%s""",
                            (row[0], row[8]))
                 
            else:
                continue
            
            c2.execute("""INSERT INTO wiki_article
                        SET id=%s,
                            title=%s,
                            content=%s,
                            created_at=%s,
                            last_update=%s,
                            content_type_id=%s,
                            object_id=%s,
                            removed=0,
                            tags=''""",
                        (row[0], title, row[1], datetime.now(), row[2], ctype, oid))
            
            c2.execute("""INSERT INTO whiteboard_whiteboard
                        SET article_ptr_id=%s,
                            parent_group_id=%s,
                            converted=0""",
                        (row[0], row[10]))
            
            if row[2] and row[9]:
                c2.execute("""INSERT INTO wiki_changeset
                            SET article_id=%s,
                                editor_id=%s,
                                editor_ip='',
                                revision=1,
                                old_title=%s,
                                content_diff='',
                                comment='',
                                modified=%s,
                                reverted=0""",
                                (row[0], row[9], title, row[2]))
            
            try:
                print "whiteboard", row[0], "named", title, "attached to", row[10]
            except:
                print "meh, couldn't print", row[0]

    def migrate_champ(self, c, c2):
        # ./manage.py reset --noinput champ ; ./manage.py migrate | tee champ.log

        c.execute("SELECT * FROM activities")
        for row in c.fetchall():
            if not row[93]:
                continue
            
            try:
                print "champ", row[0], "-", row[1]
            except:
                print "meh, couldn't print", row[0]
            
            if row[5]:
                visible = True
            else:
                visible = False
            if row[6]:
                confirmed = True
            else:
                confirmed = False 
            
            c2.execute("""INSERT INTO champ_activity
                        SET id=%s,
                            name=%s,
                            date=%s,
                            created_date=%s,
                            modified_date=%s,
                            creator_id=%s,
                            editor_id=%s,
                            group_id=%s,
                            visible=%s,
                            confirmed=%s,
                            prepHours=%s,
                            execHours=%s,
                            numVolunteers=%s""",
                            (row[0], row[1], row[2], row[3], row[4], row[92],
                             row[91], row[93], visible, confirmed, row[8], row[9], row[7]))
            
            c2.execute("""INSERT INTO champ_metrics
                        SET activity_id=%s, metric_type=%s""",
                        (row[0], "impactmetrics"))
            
            c2.execute("""INSERT INTO champ_impactmetrics
                        SET metrics_ptr_id=LAST_INSERT_ID(),
                            description=%s,
                            goals=%s,
                            outcome=%s,
                            `notes`=%s,
                            `changes`=%s,
                            `repeat`=%s""",
                            (row[10], row[11], row[12], row[13], row[14], row[15]))
            
            if row[16] == 1:
                c2.execute("""INSERT INTO champ_functioningmetrics
                            SET metrics_ptr_id=LAST_INSERT_ID(),
                                type=%s,
                                location=%s,
                                purpose=%s,
                                attendance=%s,
                                duration=%s""",
                                (row[49], row[50], row[51], row[52], row[53]))
                print "   functioning"
                
            if row[17] == 1:
                c2.execute("""INSERT INTO champ_memberlearningmetrics
                            SET metrics_ptr_id=LAST_INSERT_ID(),
                                type=%s,
                                learning_partner=%s,
                                curriculum=%s,
                                resources_by=%s,
                                duration=%s,
                                attendance=%s,
                                new_attendance=%s""",
                                (row[27], row[28], row[29], row[30], row[31],
                                 row[32], row[33]))
                print "   member learning"
                
            if row[18] == 1:
                c2.execute("""INSERT INTO champ_publicengagementmetrics
                            SET metrics_ptr_id=LAST_INSERT_ID(),
                                type=%s,
                                location=%s,
                                purpose=%s,
                                subject=%s,
                                level1=%s,
                                level2=%s,
                                level3=%s""",
                                (row[54], row[55], row[56], row[57], row[58], row[59], row[60]))
                print "   public engagement"
                
            if row[19] == 1:
                c2.execute("""INSERT INTO champ_publicadvocacymetrics
                            SET metrics_ptr_id=LAST_INSERT_ID(),
                                type=%s,
                                units=%s,
                                decision_maker=%s,
                                position=%s,
                                ewb=%s,
                                purpose=%s,
                                learned=%s""",
                                (row[61], row[62], row[63], row[64], row[65], row[66], row[67]))
                print "   public advocacy"
                
            if row[20] == 1:
                c2.execute("""INSERT INTO champ_workplaceoutreachmetrics
                            SET metrics_ptr_id=LAST_INSERT_ID(),
                                company=%s,
                                city=%s,
                                presenters=%s,
                                ambassador=%s,
                                email=%s,
                                phone=%s,
                                presentations=%s,
                                attendance=%s,
                                type=%s""",
                                (row[76], row[77], row[78], row[79], row[80],
                                 row[81], row[82], row[83], row[84]))
                print "   workplace outreach"
            
            if row[21] == 1:
                c2.execute("""INSERT INTO champ_schooloutreachmetrics
                            SET metrics_ptr_id=LAST_INSERT_ID(),
                                school_name=%s,
                                teacher_name=%s,
                                teacher_email=%s,
                                teacher_phone=%s,
                                presentations=%s,
                                students=%s,
                                grades=%s,
                                subject=%s,
                                workshop=%s,
                                facilitators=%s,
                                new_facilitators=%s,
                                notes=%s""",
                                (row[34], row[37], row[38], row[39], row[40],
                                 row[41], row[42], row[43], row[44], row[45],
                                 row[46], row[48]))
                print "   school outreach"
                
            if row[22] == 1:
                c2.execute("""INSERT INTO champ_curriculumenhancementmetrics
                            SET metrics_ptr_id=LAST_INSERT_ID(),
                                name=%s,
                                code=%s,
                                students=%s,
                                hours=%s,
                                professor=%s,
                                ce_activity=%s""",
                                (row[85], row[86], row[87], row[88], row[89], row[90]))
                print "   curriculum"
                
            if row[23] == 1:
                c2.execute("""INSERT INTO champ_publicationmetrics
                            SET metrics_ptr_id=LAST_INSERT_ID(),
                                outlet=%s,
                                type=%s,
                                location=%s,
                                circulation=%s""",
                                (row[68], row[69], row[70], row[72]))
                print "   publication"
            
            if row[24] == 1:
                c2.execute("""INSERT INTO champ_fundraisingmetrics
                            SET metrics_ptr_id=LAST_INSERT_ID(),
                                goal=%s,
                                revenue=%s""",
                                (row[73], row[74]))
                print "   fundraising"

        c.execute("SELECT * FROM reflections")
        for row in c.fetchall():
            print "champ reflection", row[0]
            c2.execute("""INSERT INTO champ_journal
                        SET id=%s,
                            date=%s,
                            creator_id=%s,
                            group_id=%s,
                            private=%s,
                            snapshot=%s,
                            highlight=%s,
                            challenge=%s,
                            leadership=%s,
                            learning=%s,
                            innovation=%s,
                            yearplan=%s,
                            office=%s""",
                            (row[0], row[10], row[11], row[12],row[9], row[1],
                             row[2], row[3], row[4], row[5], row[6], row[7],row[8]))
            
        c.execute("SELECT * FROM yearplans")
        for row in c.fetchall():
            print "champ yearplan", row[0], row[1], row[4]
            c2.execute("""INSERT INTO champ_yearplan
                        SET id=%s,
                            year=%s,
                            group_id=%s,
                            modified_date=%s,
                            last_editor_id=%s,
                            ml_average_attendance=%s,
                            ml_total_hours=%s,
                            adv_contacts=%s,
                            eng_people_reached=%s,
                            fund_total=%s,
                            pub_media_hits=%s,
                            ce_hours=%s,
                            ce_students=%s,
                            so_presentations=%s,
                            so_reached=%s,
                            wo_presentations=%s,
                            wo_reached=%s""",
                            (row[0], row[1], row[4], row[2], row[3], row[5], row[6],
                             row[7], row[8], row[9], row[10], row[11], row[12], row[13],
                             row[14], row[15], row[16]))
            
    def migrate_stats(self, c, c2):
        # ./manage.py reset --noinput stats ; ./manage.py migrate | tee stats.log
        
        c.execute("SELECT * FROM dailystats")
        for row in c.fetchall():
            print "stats", row[0], row[1]
            c2.execute("""INSERT INTO stats_dailystats
                        SET id=%s,
                            day=%s,
                            signups=%s,
                            mailinglistsignups=%s,
                            signins=%s,
                            posts=%s,
                            events=%s,
                            eventMailings=%s,
                            replies=%s,
                            whiteboardEdits=%s,
                            regupgrades=%s,
                            regdowngrades=%s,
                            deletions=%s,
                            renewals=%s,
                            mailinglistupgrades=%s,
                            users=%s,
                            regularmembers=%s,
                            associatemembers=%s,
                            activityCreations=%s,
                            activityEdits=%s,
                            activityConfirmations=%s,
                            activityDeletions=%s,
                            reflections=%s,
                            filesAdded=%s""",
                            (row[0], row[1], row[2], row[3], row[4], row[5],
                             row[12], row[13], row[6], row[14], row[7], row[8],
                             row[9], row[10], row[11], 0, 0, 0,
                             row[15], row[16], row[17], row[18], row[19], row[20]))
            