from django.contrib import admin
from finance.models import Transaction
from finance.models import  MonthlyReport
from finance.models import Income
from finance.models import Expenditure, Donation, Category, Budget, BudgetItem
#, Event


admin.site.register(MonthlyReport)
admin.site.register(Transaction)
admin.site.register(Income)
admin.site.register(Expenditure)
admin.site.register(Donation)
admin.site.register(Category)
admin.site.register(Budget)
admin.site.register(BudgetItem)

#admin.site.register(Event)
