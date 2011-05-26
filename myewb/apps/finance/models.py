#import from django
from django.db import models
from django.forms import ModelForm  #used for creating forms at bottom of page
from django.forms import forms
from django import forms
from django.contrib.auth.models import User

#import python utility
import datetime

#import from myewb
from base_groups.models import BaseGroup
from siteutils.shortcuts import get_object_or_none

from django import template
import locale
locale.setlocale(locale.LC_ALL)
register = template.Library()
 
 
@register.filter()
def currency(value):
    return locale.currency(float(value), grouping=True)

TRANSACTION_CHOICES = (
    ('donation','Donation'),
    ('fundraising_event', 'Fundraising Event'),
    ('event_cost', 'Event Cost'),
    ('conference', 'Conference'),
    ('advertising', 'Advertising'),
    ('overseas', 'Overseas'),
)

ENTEREDBY_CHOICES = (
    ('NO','National Office'),
    ('CH', 'Chapter'),
)

TYPE_CHOICES = (
    ('EX','Expenditure'),
    ('IN', 'Income'),
    ('CM', 'Commitment')
)

SUBMITTED_CHOICES = (
    ('Y','Yes'),
    ('N', 'No'),
)
DONATION_CHOICES = (
    ('Corporate','Corporate Donation'),
    ('Individual', 'Individual Donation'),
    ('Faculty', 'Faculty Donation'),
    ('University Club', 'University Club Donation'),
    ('Community','Community Donation'),
    ('Professional','Professional Association Donation'),
    ('Alumni','Alumni Donation'),
)

class MonthlyReport(models.Model):
    date = models.DateField()
    enter_date = models.DateField('Enter Date', auto_now_add=True)
    group = models.ForeignKey(BaseGroup)
    type = models.CharField(max_length = 2, default = 'NO')
    creator= models.ForeignKey(User, related_name="monthlyreport_created")
    
    def __unicode__(self):
#        return u'%s (%s) - %s %s' %(self.group.name, self.type, self.date.year, self.date.month)
        return u'%s (%s) - %s %s' %(self.group.name, self.type, self.date.year, self.date.month)

class Category(models.Model):
    name = models.CharField(max_length = 200)
    type = models.CharField(max_length = 2, choices=TYPE_CHOICES)
    slug = models.CharField(max_length = 200)
    noaccount = models.CharField(max_length = 200)
    
    def __unicode__(self):
        return self.name

class Transaction(models.Model):  
    bank_date = models.DateField('Bank Date (YYYY-MM-DD)', null=True, blank=True) 
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    description = models.CharField(max_length = 100)

#    automatic fields
    enter_date = models.DateField('Enter Date', auto_now_add=True)
    account = models.CharField(max_length = 2, choices=ENTEREDBY_CHOICES, default = 'CH')
    submitted = models.CharField(max_length = 1, choices=SUBMITTED_CHOICES, default = 'N')
    type = models.CharField(max_length = 2, choices=TYPE_CHOICES)
 
#    linked objects
#    event = models.ForeignKey(Event, null=True, blank=True) #used to link to an event
    group = models.ForeignKey(BaseGroup)
    monthlyreport = models.ForeignKey(MonthlyReport, null=True, blank=True)
    category = models.ForeignKey(Category)
    creator = models.ForeignKey(User, related_name="transactions_created")
    editor = models.ForeignKey(User, related_name="transactions_edited")   

    def __unicode__(self):
        return u'%s %s' %(self.enter_date, self.amount)
    
    def get_fields(self):
        return [(field, field.value_to_string(self)) for field in Transaction._meta.fields]

class Income(Transaction):
    
    def __unicode__(self):
        return u'%s %s' %(self.enter_date, self.amount)  
    
class Expenditure(Transaction):
    payee = models.CharField(max_length = 200)
    cheque_num = models.IntegerField('Cheque Number', null=True, blank=True)
    cheque_date = models.DateField('Cheque Date (YYYY-MM-DD)', null=True, blank=True)
    hst = models.DecimalField('HST (0.00)', max_digits=10, decimal_places=2, null=True, blank=True)
#    reciept_img = models.FileField('Receipt Image', upload_to = 'receipt_images', null=True, blank=True)
    
    def __unicode__(self):
        return u'%s %s' %(self.payee, self.amount)

class Donation(Income):
    donation_category = models.CharField(max_length = 40, choices=DONATION_CHOICES)
    donor = models.CharField(max_length = 200)
    address = models.CharField(max_length = 200)
    city = models.CharField(max_length = 50)
    province = models.CharField('Province/State', max_length = 50) 
    country = models.CharField(max_length = 200)
    postal = models.CharField('Postal Code', max_length = 200)
    cheque_date = models.DateField('Cheque Date (YYYY-MM-DD)', null=True, blank=True)
    cheque_num = models.CharField('Cheque Number', max_length=10, null=True, blank=True)
    taxreceipt = models.CharField('Tax Receipt? (Y/N)', max_length = 1)
    cheque_img = models.FileField('Cheque Image', upload_to = 'donation_cheques', null=True, blank=True)


class Budget(models.Model):
    name = models.CharField('Budget Name', max_length = 30)
    start_date = models.DateField('Start Date (YYYY-MM-DD)')
    end_date = models.DateField('End Date (YYYY-MM-DD)')
    
#    linked objects
    group = models.ForeignKey(BaseGroup)
    creator = models.ForeignKey(User, related_name="budget_created")
    edited_by = models.ForeignKey(User, related_name="budget_edited")
    
    def __unicode__(self):
        return u'%s %s-%s' %(self.name, self.start_date, self.end_date)

class BudgetItem(models.Model):

    type = models.CharField(max_length = 2, choices=TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
#    linked objects
    budget = models.ForeignKey(Budget)
    category = models.ForeignKey(Category)
    
class BudgetItemForm(forms.Form):
    amount = forms.DecimalField(max_digits=10, decimal_places=2)

class BudgetForm(ModelForm):
    class Meta:
        model = Budget
        exclude = ('group', 'creator', 'edited_by')
        
#    def clean_end_date(self):
#        end_date = self.cleaned_data['end_date']
#        start_date = self.cleaned_data['start_date']
#        
#        if start_date > end_date:
#            raise forms.ValidationError ("End date must be after start date.")

class UploadCommitmentForm(forms.Form):
    month = forms.DateField()
#    dir = forms.CharField(max_length=200)
    dir = forms.FileField(required=False)

class CreateNOReports(forms.Form):
    month = forms.DateField()

#=======================================================================================
# TRANSACTION FORM
#=======================================================================================
class TransactionForm(ModelForm):
    
    class Meta:
        model = Transaction
        exclude = ('enter_date','account')
    
    def clean_bank_date(self):
        bank_date = self.cleaned_data['bank_date']
        tdate = datetime.date.today()
        pdate = tdate.month - 2
        
        if bank_date:
            if tdate < bank_date:
                raise forms.ValidationError ("Cannot enter in a bank date in the future.")
            if bank_date.month < pdate:
                raise forms.ValidationError ("Cannot enter in a bank date from two months ago.")
        return bank_date
    
#=======================================================================================
# INCOME FORM
#=======================================================================================
class IncomeForm(ModelForm):
    
    class Meta:
        model = Income
        exclude = ('enter_date', 'type', 'monthlyreport','submitted','account', 'group', 'creator', 'editor')

    def __init__(self, *args, **kwargs):
        super(IncomeForm, self).__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(type='IN')
        
    def clean_bank_date(self):
        bank_date = self.cleaned_data['bank_date']
        tdate = datetime.date.today()
        pdate = tdate.month - 2
        
        if bank_date:
            if tdate < bank_date:
                raise forms.ValidationError ("Cannot enter in a bank date in the future.")
            if bank_date.month < pdate:
                raise forms.ValidationError ("Cannot enter in a bank date from two months ago.")
        return bank_date
    
    def clean_category(self):
        category = self.cleaned_data['category']
        
        if category.type != "IN":
            raise forms.ValidationError ("Not an income category.")
        if category.name == "donation":
            raise forms.ValidationError ("You must enter donations in the donation entry form (see left).")
        
        return category


#=======================================================================================
# INCOME EDIT FORM
#=======================================================================================
class IncomeEditForm(ModelForm):
    
    class Meta:
        model = Income
        exclude = ('enter_date','monthlyreport', 'type', 'submitted','account', 'amount', 'bank_date', 'group', 'creator', 'editor')
 
    def __init__(self, *args, **kwargs):
        super(IncomeEditForm, self).__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(type='IN')
           
    def clean_bank_date(self):
        bank_date = self.cleaned_data['bank_date']
        tdate = datetime.date.today()
        pdate = tdate.month - 2
        
        if bank_date:
            if tdate < bank_date:
                raise forms.ValidationError ("Cannot enter in a bank date in the future.")
            if bank_date.month < pdate:
                raise forms.ValidationError ("Cannot enter in a bank date from two months ago.")
        return bank_date
    
    def clean_category(self):
        category = self.cleaned_data['category']
        
        if category.type != "IN":
            raise forms.ValidationError ("Not an income category.")
        
        return category

#=======================================================================================
# INCOME STAFF FORM
#=======================================================================================
class IncomeStaffForm(ModelForm):
    
    class Meta:
        model = Income
        exclude = ('enter_date','type', 'group', 'creator', 'editor')
        
    def __init__(self, *args, **kwargs):
        super(IncomeStaffForm, self).__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(type='IN')
        
    def clean_category(self):
        category = self.cleaned_data['category']
        
        if category.type != "IN":
            raise forms.ValidationError ("Not an income category.")
        
        return category
    
    
#=======================================================================================
# EXPENDITURE FORM
#=======================================================================================

class ExpenditureForm(ModelForm):
    
    class Meta:
        model = Expenditure
        exclude = ('enter_date','monthlyreport', 'type', 'submitted','account', 'group', 'creator', 'editor')
 
    def __init__(self, *args, **kwargs):
        super(ExpenditureForm, self).__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(type='EX')
        
    def clean_bank_date(self):
        bank_date = self.cleaned_data['bank_date']
        tdate = datetime.date.today()
        pdate = tdate.month - 2
        
        if bank_date:
            if tdate < bank_date:
                raise forms.ValidationError ("Cannot enter in a bank date in the future.")
            if bank_date.month < pdate:
                raise forms.ValidationError ("Cannot enter in a bank date from two months ago.")
        return bank_date
    
    def clean_category(self):
        category = self.cleaned_data['category']
        
        if category.type != "EX":
            raise forms.ValidationError ("Not an expenditure category.")
        
        return category

#=======================================================================================
# EXPENDITURE EDIT FORM
#=======================================================================================


class ExpenditureEditForm(ModelForm):
    
    class Meta:
        model = Expenditure
        exclude = ('enter_date','monthlyreport', 'type', 'submitted','account', 'amount', 'bank_date', 'group', 'creator', 'editor')
  
    def __init__(self, *args, **kwargs):
        super(ExpenditureEditForm, self).__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(type='EX')
           
    def clean_bank_date(self):
        bank_date = self.cleaned_data['bank_date']
        tdate = datetime.date.today()
        pdate = tdate.month - 2

        if tdate < bank_date:
            raise forms.ValidationError ("Cannot enter in a bank date in the future.")
        if bank_date.month < pdate:
            raise forms.ValidationError ("Cannot enter in a bank date from two months ago.")
        return bank_date
    
    def clean_category(self):
        category = self.cleaned_data['category']
        
        if category.type != "EX":
            raise forms.ValidationError ("Not an expenditure category.")
        
        return category
    

#=======================================================================================
# EXPENDTIURE STAFF FORM
#=======================================================================================
class ExpenditureStaffForm(ModelForm):
    
    class Meta:
        model = Expenditure
        exclude = ('enter_date','type', 'group', 'creator', 'editor')
  
    def __init__(self, *args, **kwargs):
        super(ExpenditureStaffForm, self).__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(type='EX')
            
    def clean_category(self):
        category = self.cleaned_data['category']
        
        if category.type != "EX":
            raise forms.ValidationError ("Not an expenditure category.")
        
        return category

#=======================================================================================
# DONATION FORM
#=======================================================================================

class DonationEditForm(ModelForm):
    
    class Meta:
        model = Expenditure
        exclude = ('enter_date','monthlyreport', 'type', 'submitted','account', 'amount', 'bank_date', 'group', 'creator', 'editor')
    
    def clean_bank_date(self):
        bank_date = self.cleaned_data['bank_date']
        tdate = datetime.date.today()
        pdate = tdate.month - 2

        if tdate < bank_date:
            raise forms.ValidationError ("Cannot enter in a bank date in the future.")
        if bank_date.month < pdate:
            raise forms.ValidationError ("Cannot enter in a bank date from two months ago.")
        return bank_date


class DonationForm(ModelForm):
    
    class Meta:
        model = Donation
        exclude = ('enter_date','monthlyreport', 'type', 'submitted','account', 'event', 'category', 'group', 'creator', 'editor')
    
    
    def clean_bank_date(self):
        bank_date = self.cleaned_data['bank_date']
        tdate = datetime.date.today()
        pdate = tdate.month - 2

        if tdate < bank_date:
            raise forms.ValidationError ("Cannot enter in a bank date in the future.")
        if bank_date.month < pdate:
            raise forms.ValidationError ("Cannot enter in a bank date from two months ago.")
        return bank_date
    
#=======================================================================================
# DONATION STAFF FORM
#=======================================================================================
class DonationStaffForm(ModelForm):
    
    class Meta:
        model = Donation
        exclude = ('enter_date','type', 'group', 'creator', 'editor')
