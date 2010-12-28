from transactions.models import IncomeCategory, ExpenditureCategory, Income, Expenditure
from django.contrib import admin

admin.site.register(Income)
admin.site.register(Expenditure)
admin.site.register(IncomeCategory)
admin.site.register(ExpenditureCategory)