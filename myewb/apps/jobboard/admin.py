from django.contrib import admin
from jobboard.models import JobPosting, Skill, JobFilter

admin.site.register(JobPosting)
admin.site.register(Skill)
admin.site.register(JobFilter)
