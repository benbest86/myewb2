from datetime import date, timedelta

from django.core.management.base import NoArgsCommand
from django.template.loader import render_to_string

from mailer.sendmail import send_mail
from profiles.models import MemberProfile


class Command(NoArgsCommand):
    help = "Sends membership expiry reminders"

    requires_model_validation = True

    def handle_noargs(self, **options):
        msgs = []

        yesterday = date.today() - timedelta(days=1)
        oneday = date.today()
        oneweek = date.today() + timedelta(days=7)
        onemonth = date.today() + timedelta(days=31)
        
        profiles_expired = MemberProfile.objects.filter(membership_expiry=yesterday,
                                                        user2__is_active=True)
        profiles_oneday = MemberProfile.objects.filter(membership_expiry=oneday,
                                                       user2__is_active=True)
        profiles_oneweek = MemberProfile.objects.filter(membership_expiry=oneweek,
                                                        user2__is_active=True)
        profiles_onemonth = MemberProfile.objects.filter(membership_expiry=onemonth,
                                                         user2__is_active=True)

        emails = []

        msgs.append("Expiry reminders: %d" % profiles_expired.count())
        for p in profiles_expired:
            context = {"user": p.user2,
                       "profile": p}
        
            subject = render_to_string("profiles/emails/membership_expiry_subject.txt", context)
            body = render_to_string("profiles/emails/membership_expiry_body.txt", context)
            emails.append((subject, body, p.user2.email))
            
        msgs.append("One day reminders: %d" % profiles_oneday.count())
        for p in profiles_oneday:
            context = {"user": p.user2,
                       "profile": p}
        
            subject = render_to_string("profiles/emails/membership_oneday_subject.txt", context)
            body = render_to_string("profiles/emails/membership_oneday_body.txt", context)
            emails.append((subject, body, p.user2.email))
            
        msgs.append("One week reminders: %d" % profiles_oneweek.count())
        for p in profiles_oneweek:
            context = {"user": p.user2,
                       "profile": p}
        
            subject = render_to_string("profiles/emails/membership_oneweek_subject.txt", context)
            body = render_to_string("profiles/emails/membership_oneweek_body.txt", context)
            emails.append((subject, body, p.user2.email))
            
        msgs.append("One month reminders: %d" % profiles_onemonth.count())
        for p in profiles_onemonth:
            context = {"user": p.user2,
                       "profile": p}
        
            subject = render_to_string("profiles/emails/membership_onemonth_subject.txt", context)
            body = render_to_string("profiles/emails/membership_onemonth_body.txt", context)
            emails.append((subject, body, p.user2.email))

        for subject, body, email in emails:
            subject = "".join(subject.splitlines())
            send_mail(subject=subject,
                      htmlMessage=body,
                      fromemail='"Engineers Without Borders" <info@ewb.ca>',
                      recipients=[email],
                      use_template=False)

        return '\n'.join(msgs)
