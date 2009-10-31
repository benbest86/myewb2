from django.contrib import admin
from volunteering.models import *

admin.site.register(Placement)
admin.site.register(Application)
admin.site.register(Session)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(Evaluation)
admin.site.register(EvaluationCriterion)
admin.site.register(EvaluationResponse)

