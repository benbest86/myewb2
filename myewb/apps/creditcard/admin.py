"""myEWB credit card admin declarations

This file is part of myEWB
Copyright 2009 Engineers Without Borders (Canada) Organisation and/or volunteer contributors

Last modified on 2009-08-13
@author Francis Kung
"""

from django.contrib import admin
from creditcard.models import Payment, Product

#class PaymentAdmin(admin.ModelAdmin):
#    list_display = ('name', 'slug', 'creator', 'created')
    
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'amount')

admin.site.register(Product, ProductAdmin)
