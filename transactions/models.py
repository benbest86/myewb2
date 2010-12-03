#import from django
from django.db import models
from django.forms import ModelForm  #used for creating automatic forms
from django import forms

#import python utility
import datetime

#import from 461designproject

#predefined choices
TYPE_CHOICES = (
    ('EX','Expenditure'),
    ('IN', 'Income'),
)

#start model defintion
class IncomeCategory(models.Model):
    name = models.CharField(max_length = 200)
    slug = models.CharField(max_length = 200)
    
    def __unicode__(self):
        return self.name

class ExpenditureCategory(models.Model):
    name = models.CharField(max_length = 200)
    slug = models.CharField(max_length = 200)
    
    def __unicode__(self):
        return self.name

class Transaction(models.Model):  
    date = models.DateField('Date', null=True, blank=True) 
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length = 100)

#    automatic fields
    enter_date = models.DateField('Enter Date', auto_now_add=True)
    type = models.CharField(max_length = 2, choices=TYPE_CHOICES) #income or expenditure
 
#    linked objects - foreign keys go here


    def __unicode__(self):
        return u'%s %s' %(self.date, self.amount)
    
class Income(Transaction):
    income_category = models.ForeignKey(IncomeCategory)
    def __unicode__(self):
        return u'%s %s' %(self.date, self.amount)
    
class Expenditure(Transaction):
    expenditure_category = models.ForeignKey(ExpenditureCategory)
    reciept_img = models.FileField('Receipt Image', upload_to = 'receipt_images', null=True, blank=True)
    
    def __unicode__(self):
        return u'%s %s' %(self.payee, self.amount)


#forms on the website
class IncomeForm(ModelForm):
    
    class Meta:
        model = Income

class ExpenditureForm(ModelForm):
    
    class Meta:
        model = Expenditure
    
    
    