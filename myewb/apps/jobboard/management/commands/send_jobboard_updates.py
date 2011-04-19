from datetime import date, timedelta

from django.contrib.auth.models import User
from django.core.management.base import NoArgsCommand
from django.db.models import Q
from django.template.loader import render_to_string

from mailer.sendmail import send_mail
from jobboard.models import JobPosting, JobFilter


class Command(NoArgsCommand):
    help = "Sends updates that match members' job board filters"

    requires_model_validation = True

    def handle_noargs(self, **options):
        msgs = []
        emails = []

        yesterday = date.today() - timedelta(days=1)
        
        jobs = JobPosting.objects.open()
        jobs = jobs.filter(last_updated__gt=yesterday)
        jobs = jobs.filter()
        msgs.append("total updated jobs: %d" % jobs.count())
        
        users = User.objects.filter(jobfilter__email=True).distinct()
        msgs.append("total users: %d" % users.count())
        msgs.append("")
        
        for u in users:
            filters = JobFilter.objects.filter(user=u, email=True)
            alljobs = []
            
            for filter in filters:
                myjobs = jobs.all()
                
                # the easy ones
                if filter.deadline_comparison == 'lt':
                    myjobs = myjobs.filter(deadline__lte=filter.deadline)
                elif filter.deadline_comparison == 'gt':
                    myjobs = myjobs.filter(deadline__gte=filter.deadline)
                
                if filter.urgency_comparison == 'lt':
                    myjobs = myjobs.filter(urgency__lte=filter.urgency)
                elif filter.urgency_comparison == 'gt':
                    myjobs = myjobs.filter(urgency__gte=filter.urgency)
                
                if filter.time_required_comparison == 'lt':
                    myjobs = myjobs.filter(time_required__lte=filter.time_required)
                elif filter.time_required_comparison == 'gt':
                    myjobs = myjobs.filter(time_required__gte=filter.time_required)
                    
                # skills, such a pain
                if filter.skills_comparison:
                        if filter.skills_comparison == 'any':
                            myjobs = myjobs.filter(skills__in=filter.skills.all()).distinct()
                        elif filter.skills_comparison == 'all':
                            for skill in filter.skills:
                                myjobs = myjobs.filter(skills__id=skill)
                        else:
                            myjobs = myjobs.exclude(skills__in=filter.skills.all())
            
                # and locations
                if filter.location_comparison:
                    if filter.location_comparison == 'oneof':     # validate deadline2 too!
                        myjobs = myjobs.filter(location__in=filter.location).distinct()
            
                # search terms...
                if filter.search:
                    myjobs = myjobs.filter(Q(description__icontains=filter.search) | Q(name__icontains=filter.search)).distinct()
                    
                if myjobs.count():
                    alljobs.extend(myjobs)
                    
            if len(alljobs):
                uniquejobs = list(set(alljobs))
                
                context = {"user": u,
                           "jobs": uniquejobs}
                subject = render_to_string("jobboard/emails/updates_subject.txt", context)
                body = render_to_string("jobboard/emails/updates_body.txt", context)
                emails.append((subject, body, u.email))
                
                msgs.append("%s (%d filters, %d jobs, %d unique)" % (u.visible_name(), filters.count(), len(alljobs), len(uniquejobs)))
        
        for subject, body, email in emails:
            subject = "".join(subject.splitlines())
            send_mail(subject=subject,
                      htmlMessage=body,
                      fromemail='"Engineers Without Borders" <info@ewb.ca>',
                      recipients=[email],
                      use_template=False)
        
        return '\n'.join(msgs)
