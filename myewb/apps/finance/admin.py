from django.contrib import admin
from finance.models import Transaction
from finance.models import  MonthlyReport
from finance.models import Income
from finance.models import Expenditure
from finance.models import Donation
from finance.models import Category
from finance.models import Budget
from finance.models import BudgetItem
#, Event

class TransactionAdmin(admin.ModelAdmin):
    list_display = ('bank_date', 'account', 'type', 'amount', 'group', 'category', 'enter_date', 'monthlyreport')
    list_filter = ['group']
    search_fields = ['description']
    date_hierarchy = 'bank_date'

class MonthlyReportAdmin(admin.ModelAdmin):
    list_display = ('date', 'type', 'enter_date', 'group')
    list_filter = ['group']

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'slug')
    list_filter = ['type']
    

admin.site.register(MonthlyReport, MonthlyReportAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Income)
admin.site.register(Expenditure)
admin.site.register(Donation)
admin.site.register(Budget)
admin.site.register(BudgetItem)

#admin.site.register(Event)
