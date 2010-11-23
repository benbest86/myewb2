# import django stuff
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.db.models import Avg, Max, Min, Count, Sum
from django.forms.formsets import formset_factory
#import functionality
import datetime
import csv
import os
import shlex
import tempfile

from datetime import timedelta
from pygooglechart import SimpleLineChart, Axis, PieChart3D, PieChart2D, StackedHorizontalBarChart

#import your needed models here
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from base_groups.models import BaseGroup
from base_groups.decorators import group_admin_required
from networks.decorators import chapter_president_required
from networks.models import Network
from finance.models import Transaction, Income, Expenditure, Donation, MonthlyReport, Budget, BudgetItem, Category
from finance.models import IncomeForm, ExpenditureForm, TransactionForm, DonationForm, IncomeEditForm, ExpenditureEditForm, DonationEditForm, IncomeStaffForm, ExpenditureStaffForm, DonationStaffForm 
from finance.models import UploadCommitmentForm, CreateNOReports, BudgetItemForm, BudgetForm  #get the form to display
from siteutils import schoolyear
from siteutils.helpers import fix_encoding

@login_required()
def index(request, group_slug=None):
#================================================================================
# index
#================================================================================
    context = dict()
    
    if group_slug:
        group = get_object_or_404(Network, slug=group_slug)
    else:
        group = None
    
    if group:
        context['group'] = group
        context['is_group_admin'] = group.user_is_admin(request.user)
        context['is_president'] = group.user_is_president(request.user)
    
    context['allgroups'] = Network.objects.filter(chapter_info__isnull=False, is_active=True).order_by('name')
    
    return render_to_response('finance/index.htm',context, context_instance=RequestContext(request))

@group_admin_required()
def create_income(request, group_slug):
#======================================================
#CREATE Income
#======================================================
    #    get chapter
    group = get_object_or_404(Network, slug=group_slug)
    trans_chap, income_chap, donations_chap, expenditure_chap, monthly_chap = create_chapter_filters(group_slug)
    template_data = dict()
    
    if request.method == 'POST': # If the form has been submitted...
#        if the user is staff, then be able to see all the fields
        if request.user.is_staff:
            form = IncomeStaffForm(request.POST)
        else:
            form = IncomeForm(request.POST) # A form bound to the POST data

        #validate fields
        if form.is_valid(): # check if fields validated
                cleaned_data = form.cleaned_data
                 
                # Process the data in form.cleaned_data
                income = form.save(commit=False) #save it to the db 
                income.type = 'IN'
                income.group = group
                income.creator = request.user
                income.editor = request.user
                income.save()
    
                return HttpResponseRedirect(reverse('summary', kwargs={'group_slug': group.slug}) ) # Redirect after POST
    else:
#       if the user is staff, they should always be able to change all fields
        if request.user.is_staff:
            form = IncomeStaffForm()
        else:
            form = IncomeForm() # A blank unbound form
        
    outstanding = income_chap.filter(bank_date__isnull=True).order_by('enter_date')
    
    template_data["form"] = form #pass the form to template as "form" variable
    template_data["trans_outstanding"] = outstanding
    template_data['group'] = group
    template_data['is_group_admin'] = group.user_is_admin(request.user)
    template_data['is_president'] = group.user_is_president(request.user)
    
    return render_to_response('finance/create_income.htm', template_data, context_instance=RequestContext(request))

@group_admin_required()
def create_expenditure(request, group_slug):
#======================================================
#CREATE Expenditure
#======================================================
    #    get chapter
    group = get_object_or_404(Network, slug=group_slug)
    trans_chap, income_chap, donations_chap, expenditure_chap, monthly_chap = create_chapter_filters(group_slug)    
    template_data = dict()
    
    if request.method == 'POST': # If the form has been submitted...
        if request.user.is_staff:
            form = ExpenditureStaffForm(request.POST)
        else:
            form = ExpenditureForm(request.POST) # A form bound to the POST data

        #validate fields
        if form.is_valid(): # check if fields validated
                cleaned_data = form.cleaned_data
                 
                # Process the data in form.cleaned_data
                exp = form.save(commit=False) #save it to the db 
                exp.type = 'EX'
                exp.group = group
                exp.creator = request.user
                exp.editor = request.user
                exp.save()
    
                return HttpResponseRedirect(reverse('summary', kwargs={'group_slug': group.slug}) ) # Redirect after POST
    else:
#        if the user is staff, then be able to see all the fields
        if request.user.is_staff:
            form = ExpenditureStaffForm() # A blank unbound form
        else:
            form = ExpenditureForm() # A blank unbound form
        
    outstanding = expenditure_chap.filter(bank_date__isnull=True).order_by('enter_date')
    
    template_data["form"] = form #pass the form to template as "form" variable
    template_data["trans_outstanding"] = outstanding
    template_data['group'] = group
    template_data['is_group_admin'] = group.user_is_admin(request.user)
    template_data['is_president'] = group.user_is_president(request.user)
    
    return render_to_response('finance/create_expenditure.htm', template_data, context_instance=RequestContext(request))

@group_admin_required()
def create_donation(request, group_slug):
#======================================================
#CREATE donation
#======================================================
    #    get chapter
    group = get_object_or_404(Network, slug=group_slug)
    trans_chap, income_chap, donations_chap, expenditure_chap, monthly_chap = create_chapter_filters(group_slug)    
    template_data = dict()
    
    if request.method == 'POST': # If the form has been submitted...
        if request.user.is_staff:
            form = DonationStaffForm(request.POST, request.FILES)
        else:
            form = DonationForm(request.POST, request.FILES) # A form bound to the POST data
        
        donation_category = Category.objects.get(name="Donation")
        #validate fields
        if form.is_valid(): # check if fields validated
                cleaned_data = form.cleaned_data
                # Process the data in form.cleaned_data
                donation = form.save(commit=False)
                donation.category = donation_category
                donation.type = 'IN'
                donation.group = group
                donation.creator = request.user
                donation.editor = request.user
                donation.save()
                
                return HttpResponseRedirect(reverse('summary', kwargs={'group_slug': group.slug}) ) # Redirect after POST
    else:
        if request.user.is_staff:
            form = DonationStaffForm()
        else:
            form = DonationForm() # A blank unbound form
        
    outstanding = donations_chap.filter(bank_date__isnull=True).order_by('enter_date')
    
    template_data["form"] = form #pass the form to template as "form" variable
    template_data["trans_outstanding"] = outstanding    
    template_data['group'] = group
    template_data['is_group_admin'] = group.user_is_admin(request.user)
    template_data['is_president'] = group.user_is_president(request.user)
    
    return render_to_response('finance/create_donation.htm', template_data, context_instance=RequestContext(request))

def create_chapter_filters(group_slug):
    trans_chap = Transaction.objects.filter(group__slug = group_slug)
    income_chap = Income.objects.filter(group__slug = group_slug)
    expenditure_chap = Expenditure.objects.filter(group__slug = group_slug)
    monthly_chap = MonthlyReport.objects.filter(group__slug = group_slug)
    donations_chap = Donation.objects.filter(group__slug = group_slug)

    return trans_chap, income_chap, donations_chap, expenditure_chap, monthly_chap

def date_prevnext(date):
    
    if date.month == 1:
        prev_date = datetime.date(year=date.year-1, month=12, day=1)
    else:
        next_date = datetime.date(year=date.year, month=date.month+1, day=1)
    
    if date.month == 12:
        prev_date = datetime.date(year=date.year+1, month=1, day=1) 
    else:
        prev_date = datetime.date(year=date.year, month=date.month-1, day=1)
    
    return prev_date, next_date

def create_category_charts(expenditure_category, income_category):
    #===========================================================================
    # chart stuff 
    #===========================================================================
    category = []
    categoryamount = []
    incomecategorylist = income_category
    for c in incomecategorylist:
        categoryamount.append(int(c['totalcategory']))
#        percent = c['totalcategory'] / income_total['total'] * 100
        category.append(c['category__name'])                              
#        category.append('%s (%d%%)' % (c['category__name'], percent))
    
    incomecategoryBreakdownChart = PieChart3D(375, 125)
    incomecategoryBreakdownChart.add_data(categoryamount)

    #categoryBreakdownChart.set_colours(['ff0000', 'ffff00', '00ff00'])
    incomecategoryBreakdownChart.set_pie_labels(category)
    incomeChart = incomecategoryBreakdownChart.get_url()
    
    category = []
    categoryamount = []
    expenditurecategorylist = expenditure_category
    for c in expenditurecategorylist:
        categoryamount.append(int(c['totalcategory']))                                
        category.append(c['category__name'])
    #categorys = sorted(categorys)
    
    expenditurecategoryBreakdownChart = PieChart3D(375, 125)
    expenditurecategoryBreakdownChart.add_data(categoryamount)
    
    #categoryBreakdownChart.set_colours(['ff0000', 'ffff00', '00ff00'])
    expenditurecategoryBreakdownChart.set_pie_labels(category)
    expenditureChart = expenditurecategoryBreakdownChart.get_url()
    
    return incomeChart, expenditureChart

@group_admin_required()
def summary(request, group_slug, year=None, month=None):
#================================================================================
# summary of transactions
#================================================================================
    #    get chapter
    group = get_object_or_404(Network, slug=group_slug)
    trans_chap, income_chap, donations_chap, expenditure_chap, monthly_chap = create_chapter_filters(group_slug)
    
    template_data = dict()
    
   #============================================================================
   # figure out account balances, outstanding transactions
   #============================================================================

#    determine account balances
    ch_in = income_chap.filter(account="CH", bank_date__isnull=False).exclude(type = 'CM').aggregate(total=Sum('amount'))
    ch_ex = expenditure_chap.filter(account="CH", bank_date__isnull=False).exclude(type = 'CM').aggregate(total=Sum('amount'))
    chapter = trans_chap.filter(account="CH", bank_date__isnull=False).exclude(type = 'CM').aggregate(last_update=Max('bank_date'))
 
 #    if either of the totals is None, switch to 0    
    if not ch_in["total"]: 
        ch_in["total"] = 0
    if not ch_ex["total"]: 
        ch_ex["total"] = 0
        
    chapter_balance = ch_in["total"] - ch_ex["total"] 
    
    no_in = income_chap.filter(account="NO", bank_date__isnull=False).exclude(type = 'CM').aggregate(total=Sum('amount'))
    no_ex = expenditure_chap.filter(account="NO", bank_date__isnull=False).exclude(type = 'CM').aggregate(total=Sum('amount'))
    national = trans_chap.filter(account="NO", bank_date__isnull=False).exclude(type = 'CM').aggregate(last_update=Max('bank_date'))
    
#    if either of the totals is None, switch to 0    
    if not no_in["total"]: 
        no_in["total"] = 0
    if not no_ex["total"]: 
        no_ex["total"] = 0
    
    national_balance = no_in["total"] - no_ex["total"]
    
    outstanding_in = income_chap.filter(account="CH", bank_date__isnull=True).exclude(type = 'CM').aggregate(total=Sum('amount'), last_update=Max('enter_date'))
    outstanding_ex = expenditure_chap.filter(account="CH", bank_date__isnull=True).exclude(type = 'CM').aggregate(total=Sum('amount'), last_update=Max('enter_date'))
    
    #    if either of the totals is None, switch to 0    
    if not outstanding_in["total"]: 
        outstanding_in["total"] = 0
    if not outstanding_ex["total"]: 
        outstanding_ex["total"] = 0
    
    total_bank_balance = chapter_balance + national_balance
    total_balance = total_bank_balance + outstanding_in["total"] - outstanding_ex["total"]
    
#===============================================================================
#     determine category breakdown
#===============================================================================
    if year:
        template_data['year'] = year
        if month:
            income_chap = income_chap.filter(bank_date__year=year, bank_date__month=month)
            expenditure_chap = expenditure_chap.filter(bank_date__year=year, bank_date__month=month)
            date = datetime.date(year=int(year), month=int(month), day=1)
            template_data['month'] = date
            template_data['prev_month'], template_data['next_month'] = date_prevnext(date)
        else:
            income_chap = income_chap.filter(bank_date__year=year)
            expenditure_chap = expenditure_chap.filter(bank_date__year=year)
    
    if trans_chap:
        template_data['empty'] = False
        income_category = income_chap.values('category__name').annotate(totalcategory=Sum('amount'))
        template_data["income_category"] = income_category
        income_total = income_chap.aggregate(total = Sum('amount'))
        template_data["income_total"] = income_total
        expenditure_category = expenditure_chap.values('category__name').annotate(totalcategory=Sum('amount'))
        template_data["expenditure_category"] = expenditure_category
        expenditure_total = expenditure_chap.aggregate(total = Sum('amount'))
        template_data["expenditure_total"] = expenditure_total
        try:
            incomeChart, expenditureChart = create_category_charts(expenditure_category, income_category)
        except:
            incomeChart = None
            expenditureChart = None
    else:
        template_data['empty'] = True
        incomeChart = None
        expenditureChart = None
        
#    charts
#    incomeChart, expenditureChart = create_category_charts(expenditure_category, income_category)
    
    template_data["income_chart"] = incomeChart
    template_data["expenditure_chart"] = expenditureChart
    
#===============================================================================
# determine the per month breakdown   
#===============================================================================
    submitted = []
    count = -1
    mr = monthly_chap.filter(type = "CH").order_by('date')
    for m in mr:
#       chapter summary
        submitted.append([])
        count = count + 1
        in_month = trans_chap.filter(monthlyreport = m.id, type = "IN").aggregate(total = Sum('amount'))
#        TODO: figure out if we want commitments in this measure or not
        ex_month = trans_chap.filter(monthlyreport = m.id).exclude(type = "IN").aggregate(total = Sum('amount'))
        date = m.date
        submitted[count].append(m.id)
        submitted[count].append(date)
#    if either of the totals is None, switch to 0    
        if not in_month["total"]: 
            in_month["total"] = 0
        if not ex_month["total"]: 
            ex_month["total"] = 0
#        append to the list    
        submitted[count].append(in_month)
        submitted[count].append(ex_month)
        submitted[count].append(in_month["total"] - ex_month["total"])
    
#    determine unsubmitted transactions
    unsubmitted = []    
    trans = trans_chap.filter(submitted = "N", bank_date__isnull=False).order_by('bank_date')
    min_transaction = trans.aggregate(min_bankdate = Min('bank_date'))
    min_date = min_transaction["min_bankdate"]
    if min_date:
        income_new = trans.filter(bank_date__year = min_date.year, bank_date__month = min_date.month, type = "IN").aggregate(total = Sum('amount'))
        expenditure_new = trans.filter(bank_date__year = min_date.year, bank_date__month = min_date.month).exclude(type = "IN").aggregate(total = Sum('amount'))
    else:
        income_new = dict()
        expenditure_new = dict()
        income_new["total"] = 0
        expenditure_new["total"] = 0
#    if either of the totals is None, switch to 0    
    if not income_new["total"]: 
        income_new["total"] = 0
    if not expenditure_new["total"]: 
        expenditure_new["total"] = 0
    
    unsubmitted.append(min_date)
    unsubmitted.append(income_new)
    unsubmitted.append(expenditure_new)
    unsubmitted.append(income_new["total"] - expenditure_new["total"])  
    
#    template passing
    template_data["chapter_in"] = ch_in
    template_data["chapter_out"] = ch_ex
    template_data["chapter_balance"] = chapter_balance
    template_data["ch_lastupdate"] = chapter["last_update"]
    
    template_data["national_in"] = no_in
    template_data["national_out"] = no_ex
    template_data["national_balance"] = national_balance
    template_data["no_lastupdate"] = national["last_update"]
    
    template_data["total_bank_balance"] = total_bank_balance
    template_data["total_balance"] = total_balance
    
    template_data["outstanding_in"] = outstanding_in
    template_data["outstanding_ex"] = outstanding_ex
    template_data["outstanding_in_lastupdate"] = outstanding_in["last_update"]
    template_data["outstanding_ex_lastupdate"] = outstanding_ex["last_update"]
    
    template_data["today"] = datetime.date.today()
    template_data["date_summary"] = submitted
    template_data["unsubmitted"] = unsubmitted
    
    template_data['group'] = group
    template_data['is_group_admin'] = group.user_is_admin(request.user)
#    template_data['is_president'] = group.user_is_president(request.user)
    
    return render_to_response('finance/summary.htm', template_data, context_instance=RequestContext(request))

@staff_member_required
def summary_no(request, year=None, month=None):
#    trans_chap = Transaction.objects.filter(bank_date__lte = datetime.date.today())
    trans_chap = Transaction.objects.all()
    income_chap = Income.objects.all()
    expenditure_chap = Expenditure.objects.all()
    donations_chap = Donation.objects.all()
    monthly_chap = MonthlyReport.objects.all()
        
    template_data = dict()

#    determine account balances
    ch_in = income_chap.filter(bank_date__isnull = False, account="CH").aggregate(total=Sum('amount'))
    ch_ex = expenditure_chap.filter(bank_date__isnull = False, account="CH").aggregate(total=Sum('amount'))
    chapter = trans_chap.filter(bank_date__isnull = False, account="CH").aggregate(last_update=Max('bank_date'))
 
 #    if either of the totals is None, switch to 0    
    if not ch_in["total"]: 
        ch_in["total"] = 0
    if not ch_ex["total"]: 
        ch_ex["total"] = 0
        
    chapter_balance = ch_in["total"] - ch_ex["total"] 
    
    no_in = income_chap.filter(account="NO", bank_date__isnull=False).exclude(type = 'CM').aggregate(total=Sum('amount'))
    no_ex = expenditure_chap.filter(account="NO", bank_date__isnull=False).exclude(type = 'CM').aggregate(total=Sum('amount'))
    national = trans_chap.filter(account="NO", bank_date__isnull=False).exclude(type = 'CM').aggregate(last_update=Max('bank_date'))
    
#    if either of the totals is None, switch to 0    
    if not no_in["total"]: 
        no_in["total"] = 0
    if not no_ex["total"]: 
        no_ex["total"] = 0
    
    national_balance = no_in["total"] - no_ex["total"]
    
    outstanding_in = income_chap.filter(account="CH", bank_date__isnull=True).exclude(type = 'CM').aggregate(total=Sum('amount'), last_update=Max('enter_date'))
    outstanding_ex = expenditure_chap.filter(account="CH", bank_date__isnull=True).exclude(type = 'CM').aggregate(total=Sum('amount'), last_update=Max('enter_date'))
    
    #    if either of the totals is None, switch to 0    
    if not outstanding_in["total"]: 
        outstanding_in["total"] = 0
    if not outstanding_ex["total"]: 
        outstanding_ex["total"] = 0
    
    total_bank_balance = chapter_balance + national_balance
    total_balance = total_bank_balance + outstanding_in["total"] - outstanding_ex["total"]
    
    
    
#    now determine category breakdown
    if year:
        template_data['year'] = year
        if month:
            income_chap = income_chap.filter(bank_date__year=year, bank_date__month=month)
            expenditure_chap = expenditure_chap.filter(bank_date__year=year, bank_date__month=month)
            date = datetime.date(year=int(year), month=int(month), day=1)
            template_data['month'] = date
            template_data['prev_month'], template_data['next_month'] = date_prevnext(date)
        else:
            income_chap = income_chap.filter(bank_date__year=year)
            expenditure_chap = expenditure_chap.filter(bank_date__year=year)
        
    
    template_data['today'] = datetime.date.today()
    
    
    if trans_chap:
        template_data['empty'] = False
        income_category = income_chap.filter(bank_date__isnull=False).values('category__name').annotate(totalcategory=Sum('amount'))
        income_total = income_chap.filter(bank_date__isnull=False).aggregate(total = Sum('amount'))
        expenditure_category = expenditure_chap.filter(bank_date__isnull=False).values('category__name').annotate(totalcategory=Sum('amount'))
        expenditure_total = expenditure_chap.filter(bank_date__isnull=False).aggregate(total = Sum('amount'))
        
        if not income_total["total"]: 
            income_total["total"] = 0
        if not expenditure_total["total"]: 
            expenditure_total["total"] = 0
        
        template_data["expenditure_category"] = expenditure_category
        template_data["income_total"] = income_total['total']
        template_data["expenditure_total"] = expenditure_total['total']
        template_data["income_category"] = income_category
        template_data['net'] = income_total['total'] - expenditure_total['total']
    else:
        template_data['empty'] = True 

    try: 
        incomeChart, expenditureChart = create_category_charts(expenditure_category, income_category)
    except:
        incomeChart = None
        expenditureChart = None

    template_data["income_chart"] = incomeChart
    template_data["expenditure_chart"] = expenditureChart
    
#    template passing
    template_data["chapter_in"] = ch_in
    template_data["chapter_out"] = ch_ex
    template_data["chapter_balance"] = chapter_balance
    template_data["ch_lastupdate"] = chapter["last_update"]
    
    template_data["national_in"] = no_in
    template_data["national_out"] = no_ex
    template_data["national_balance"] = national_balance
    template_data["no_lastupdate"] = national["last_update"]
    
    template_data["total_bank_balance"] = total_bank_balance
    template_data["total_balance"] = total_balance
    
    template_data["outstanding_in"] = outstanding_in
    template_data["outstanding_ex"] = outstanding_ex
    template_data["outstanding_in_lastupdate"] = outstanding_in["last_update"]
    template_data["outstanding_ex_lastupdate"] = outstanding_ex["last_update"]

    return render_to_response('finance/summary_no.htm', template_data, context_instance=RequestContext(request))

@group_admin_required()
def view(request, group_slug, year=None, month=None):
#======================================================
#view all transactions
#======================================================
    #    get chapter
    group = get_object_or_404(Network, slug=group_slug)
    trans_chap, income_chap, donations_chap, expenditure_chap, monthly_chap = create_chapter_filters(group_slug)
    
    template_data = dict()
    
#    income information
    incomes = income_chap.exclude(type = 'CM')
    if year:
        incomes.filter(bank_date__year = year)
        if month:
            incomes.filter(bank_date__month = month)
    
    total_in = incomes.aggregate(total=Sum('amount'))
    
#    expenditure information
    expenditures = expenditure_chap.exclude(type = 'CM')
    if year:
        expenditures.filter(bank_date__year = year)
        if month:
            expenditures.filter(bank_date__month = month)
    
    total_ex = expenditures.aggregate(total=Sum('amount'))

#    if either of the totals is None, switch to 0    
    if not total_in["total"]: 
        total_in["total"] = 0
    if not total_ex["total"]: 
        total_ex["total"] = 0    

#    all transactions
    trans = trans_chap.exclude(type = 'CM').order_by('-bank_date')
    if year:
        trans = trans.filter(bank_date__year = year)
        if month:
            trans = trans.filter(bank_date__month = month)
        
#    information to pass to template
    template_data["incomes"] = incomes
    template_data["expenditures"] = expenditures
    template_data["total_in"] = total_in
    template_data["total_ex"] = total_ex
    template_data["trans"] = trans
    template_data["month"] = month
    template_data["year"] = year
    template_data["net"] = total_in["total"] - total_ex["total"]
    template_data["today"] = datetime.date.today()
    
    template_data['group'] = group
    template_data['is_group_admin'] = group.user_is_admin(request.user)
#    template_data['is_president'] = group.user_is_president(request.user)
    
    return render_to_response('finance/view.htm', template_data, context_instance=RequestContext(request))

@group_admin_required()
def view_donations(request, group_slug, year=None, month=None):
#======================================================
#view all transactions
#======================================================
    #    get chapter
    group = get_object_or_404(Network, slug=group_slug)
    trans_chap, income_chap, donations_chap, expenditure_chap, monthly_chap = create_chapter_filters(group_slug)
    template_data = dict()
    
#    donation information
    donations = donations_chap
    
    if year:
        donations = donations.filter(bank_date__year=year)
        if month:
            donations = donations.filter(bank_date__month=month)
    
    donationtot = donations.aggregate(total = Sum('amount'))
    donations_category = donations.values('donation_category').annotate(totalcategory=Sum('amount'))
    
    template_data["donations"] = donations
    template_data["total"] = donationtot["total"]
    template_data["donations_category"] = donations_category
    
    template_data['group'] = group
    template_data['is_group_admin'] = group.user_is_admin(request.user)
#    template_data['is_president'] = group.user_is_president(request.user)
    
    return render_to_response('finance/view_donation.htm', template_data, context_instance=RequestContext(request))

@group_admin_required()
def view_commitments(request, group_slug):
#======================================================
#view all transactions
#======================================================
    #    get chapter
    group = get_object_or_404(Network, slug=group_slug)
    trans_chap, income_chap, donations_chap, expenditure_chap, monthly_chap = create_chapter_filters(group_slug)
    
    template_data = dict()
    
#    income information
    today = datetime.date.today()
    commitments = trans_chap.filter(type = "CM")
    
    template_data["commitments"] = commitments
    
    template_data['group'] = group
    template_data['is_group_admin'] = group.user_is_admin(request.user)
#    template_data['is_president'] = group.user_is_president(request.user)
    
    return render_to_response('finance/view_commitment.htm', template_data, context_instance=RequestContext(request))

@group_admin_required()
def view_id(request, group_slug, id):
#======================================================
#view specific transaction
#======================================================
    #    get chapter
    group = get_object_or_404(Network, slug=group_slug)
    trans_chap, income_chap, donations_chap, expenditure_chap, monthly_chap = create_chapter_filters(group_slug)
    template_data = dict()
    
    transaction = trans_chap.get(pk=id)
    if transaction.category.name == "Donation":
        transaction = donations_chap.get(pk=id)
    elif transaction.type == "EX":
        transaction = expenditure_chap.get(pk=id)
    elif transaction.type == "IN":
        transaction = income_chap.get(pk=id)
    
#    information to pass to template
    template_data["trans"] = transaction
    
    template_data['group'] = group
    template_data['is_group_admin'] = group.user_is_admin(request.user)
    template_data['is_president'] = group.user_is_president(request.user)
    
    return render_to_response('finance/view_detail.htm', template_data, context_instance=RequestContext(request))

@group_admin_required()
def filter(request, group_slug):
#======================================================
#filter home page
#======================================================
    #    get chapter
    group = get_object_or_404(Network, slug=group_slug)
    trans_chap, income_chap, donations_chap, expenditure_chap, monthly_chap = create_chapter_filters(group_slug)
    template_data = dict()
#    get all fields names of the first transaction
#    TODO: make it expenditure/income/donation independent
    transactions = trans_chap.get(pk=1)
    template_data["trans"] = transactions
    
    template_data['group'] = group
    template_data['is_group_admin'] = group.user_is_admin(request.user)
    template_data['is_president'] = group.user_is_president(request.user)
    
    return render_to_response('finance/filter.htm', template_data, context_instance=RequestContext(request))

@group_admin_required()
def filterfield(request, field, group_slug):
#======================================================
#filter by field
#======================================================
    #    get chapter
    group = get_object_or_404(Network, slug=group_slug)
    trans_chap, income_chap, donations_chap, expenditure_chap, monthly_chap = create_chapter_filters(group_slug)
    template_data = dict()
    
    transactions = trans_chap.values_list(field).distinct()
#    transactions = trans_chap.values_list('%s' % (field)).distinct()
    
    template_data["trans"] = transactions
    template_data["field"] = field
    
    template_data['group'] = group
    template_data['is_group_admin'] = group.user_is_admin(request.user)
    template_data['is_president'] = group.user_is_president(request.user)
    
    return render_to_response('finance/filterfield.htm', template_data, context_instance=RequestContext(request))

@group_admin_required()
def filterfieldval(request, field, value, group_slug):
#================================================================================
# filter with field and value
#================================================================================
    #    get chapter
    group = get_object_or_404(Network, slug=group_slug)
    trans_chap, income_chap, donations_chap, expenditure_chap, monthly_chap = create_chapter_filters(group_slug)
    template_data = dict()

    kwargs = {'%s' % (field): value}
    
    transactions = trans_chap.filter(**kwargs)
    total = transactions.aggregate(total=Sum('amount'))

    template_data["trans"] = transactions
    template_data["total"] = total  
    template_data["field"] = field
    template_data["value"] = value    
    
    template_data['group'] = group
    template_data['is_group_admin'] = group.user_is_admin(request.user)
    template_data['is_president'] = group.user_is_president(request.user)
    
    return render_to_response('finance/filterfieldval.htm', template_data, context_instance=RequestContext(request))

@group_admin_required()
def edit(request, group_slug):
#===============================================================================
# Edit transactions - General
#===============================================================================
    #    get chapter
    group = get_object_or_404(Network, slug=group_slug)
    trans_chap, income_chap, donations_chap, expenditure_chap, monthly_chap = create_chapter_filters(group_slug)
    template_data = dict()
    
    transactions = trans_chap.filter(submitted='N', bank_date__isnull=False).order_by('-bank_date')
    transactions_old = trans_chap.filter(submitted='Y', bank_date__isnull=False).order_by('-bank_date')[:10]
    
    outstanding = trans_chap.filter(bank_date__isnull=True).order_by('enter_date')
    
    template_data["trans"] = transactions
    template_data["trans_old"] = transactions_old
    template_data["trans_outstanding"] = outstanding
    
    template_data['group'] = group
    template_data['is_group_admin'] = group.user_is_admin(request.user)
    template_data['is_president'] = group.user_is_president(request.user)
    
    return render_to_response('finance/edit.htm', template_data, context_instance=RequestContext(request))

@group_admin_required()
def edit_id(request, id, group_slug):
#======================================================
#edit a specific Transaction
#======================================================
    #    get chapter
    group = get_object_or_404(Network, slug=group_slug)
    trans_chap, income_chap, donations_chap, expenditure_chap, monthly_chap = create_chapter_filters(group_slug)
    template_data = dict()
    t = trans_chap.get(pk=id)
    user = request.user
    
#    if income, then use all Income forms
    if t.type == "IN":
        t = get_object_or_404(Income, pk=id)
        if request.method == 'POST': # If the form has been submitted...       
            if t.category.slug == "donation":
                t = get_object_or_404(Donation, pk=id)
#                if the user is staff, they should always be able to change all fields
                if user.is_staff:
                    form = DonationStaffForm(request.POST, instance=t)
                else:
#            if it has already been submitted, limit fields
                    if t.submitted == "N":
                        form = DonationForm(request.POST, instance=t)
                    else:
                        form = DonationEditForm(request.POST, instance=t) # A form bound to the POST data
            else:
#                if the user is staff, they should always be able to change all fields
                if user.is_staff:
                    form = IncomeStaffForm(request.POST, instance=t)
                else:
#            if it has already been submitted, limit fields
                    if t.submitted == "N":
                        form = IncomeForm(request.POST, instance=t)
                    else:
                        form = IncomeEditForm(request.POST, instance=t) # A form bound to the POST data
    
            #validate fields
            if form.is_valid(): # check if fields validated
                cleaned_data = form.cleaned_data
                form = form.save(commit=False) #save it to the db
                form.editor = request.user
                form.save()
        
                return HttpResponseRedirect(reverse('view', kwargs={'group_slug': group.slug}) ) # Redirect after POST
        else:
            if t.category.slug == "donation":
                t = get_object_or_404(Donation, pk=id)
                if user.is_staff:
                    form = DonationStaffForm(instance=t)
                else:
#            if it has already been submitted, limit fields
                    if t.submitted == "N":
                        form = DonationForm(instance=t)
                    else:
                        form = DonationEditForm(instance=t) # A form bound to the POST data
            else:    
#                if the user is staff, they should always be able to change all fields
                if user.is_staff:
                    form = IncomeStaffForm(instance=t)
                else:
    #           if it has already been submitted, limit fields
                    if t.submitted == "N":
                        form = IncomeForm(instance=t)
                    else:
                        form = IncomeEditForm(instance=t)
                
#    if expenditure then use expenditure forms
    else:
        t = get_object_or_404(Expenditure, pk=id)
        if request.method == 'POST': # If the form has been submitted...
            
#                if the user is staff, they should always be able to change all fields
            if user.is_staff:
                form = ExpenditureStaffForm(request.POST, instance=t)
            else:
            
#            if it has already been submitted, limit fields
                if t.submitted == "N":
                    form = ExpenditureForm(request.POST, instance=t)
                else:
                    form = ExpenditureEditForm(request.POST, instance=t) # A form bound to the POST data
    
#            validate fields
            if form.is_valid(): # check if fields validated
                cleaned_data = form.cleaned_data
                form = form.save(commit=False) #save it to the db 
                form.editor = request.user
                form.save()
        
                return HttpResponseRedirect(reverse('view', kwargs={'group_slug': group.slug}) ) # Redirect after POST
        else:
#                if the user is staff, they should always be able to change all fields
            if user.is_staff:
                form = ExpenditureStaffForm(instance=t)
            else:
#            if it has already been submitted, limit fields
                if t.submitted == "N":
                    form = ExpenditureForm(instance=t)
                else:
                    form = ExpenditureEditForm(instance=t)
                    
    template_data["t"] = t
    template_data["form"] = form #pass the form to template as "form" variable
    
    template_data['group'] = group
    template_data['is_group_admin'] = group.user_is_admin(request.user)
    template_data['is_president'] = group.user_is_president(request.user)
    
    return render_to_response('finance/edit_id.htm', template_data, context_instance=RequestContext(request))

@group_admin_required()
def edit_all(request, group_slug):
#===============================================================================
# Edit transactions - General
#===============================================================================
    #    get chapter
    group = get_object_or_404(Network, slug=group_slug)
    trans_chap, income_chap, donations_chap, expenditure_chap, monthly_chap = create_chapter_filters(group_slug)
    template_data = dict()
    
    transactions = trans_chap.filter(submitted='N', bank_date__isnull=False).order_by('-bank_date')
    transactions_old = trans_chap.filter(submitted='Y', bank_date__isnull=False).order_by('-bank_date')
    
    outstanding = trans_chap.filter(bank_date__isnull=True).order_by('enter_date')
    
    template_data["trans"] = transactions
    template_data["trans_old"] = transactions_old
    template_data["trans_outstanding"] = outstanding
    
    template_data['group'] = group
    template_data['is_group_admin'] = group.user_is_admin(request.user)
    template_data['is_president'] = group.user_is_president(request.user)
    
    return render_to_response('finance/edit_all.htm', template_data, context_instance=RequestContext(request))

@group_admin_required()
def delete_id(request, id, group_slug):
#===============================================================================
# DELETE transactions
#===============================================================================
    #    get chapter
    group = get_object_or_404(Network, slug=group_slug)
    trans_chap, income_chap, donations_chap, expenditure_chap, monthly_chap = create_chapter_filters(group_slug)
    template_data = dict()
    
    t = trans_chap.get(pk=id)
    permission = False
    delete = False
    
#    if user is staff, then can delete anything
    if request.user.is_staff:
        t.delete()
        permission = True
        delete = True
#    make sure they have permission to delete (submitted, chapter)
    else:
        if t.account == "CH":
            if t.submitted == "N":
                if t.group.slug == group.slug:
                    t.delete()
                    permission = True
                    delete = True
                
                
    template_data["confirm"] = False
    template_data["trans"] = t
    template_data["permission"] = permission
    template_data["delete"] = delete
    
    template_data['group'] = group
    template_data['is_group_admin'] = group.user_is_admin(request.user)
    template_data['is_president'] = group.user_is_president(request.user)
    
    return render_to_response('finance/delete_id.htm', template_data, context_instance=RequestContext(request))

@group_admin_required()
def confirm_delete_id(request, id, group_slug):
#===============================================================================
# DELETE transactions
#===============================================================================
    #    get chapter
    group = get_object_or_404(Network, slug=group_slug)
    trans_chap, income_chap, donations_chap, expenditure_chap, monthly_chap = create_chapter_filters(group_slug)
    template_data = dict()
    
    t = trans_chap.get(pk=id)
    permission = False

#    make sure they have permission to delete (submitted, chapter)
    if request.user.is_staff:
            permission = True 
    else:
        if t.account == "CH":
            if t.submitted == "N":
                if t.group.slug == group.slug:
                    permission = True

                
    template_data["confirm"] = True
    template_data["trans"] = t
    template_data["permission"] = permission

    template_data['group'] = group
    template_data['is_group_admin'] = group.user_is_admin(request.user)
    template_data['is_president'] = group.user_is_president(request.user)
    
    return render_to_response('finance/delete_id.htm', template_data, context_instance=RequestContext(request))

def page_not_found(request):
#======================================================
#page not found
#======================================================
    template_data = dict()
    
    return render_to_response('finance/page_not_found.htm', template_data, context_instance=RequestContext(request))

@group_admin_required()
def monthlyreports(request, group_slug):
#======================================================
#Monthly report viewer
#======================================================
    #    get chapter
    group = get_object_or_404(Network, slug=group_slug)
    trans_chap, income_chap, donations_chap, expenditure_chap, monthly_chap = create_chapter_filters(group_slug)
    template_data = dict()
    
    chapter_monthlyreports = monthly_chap.filter(type="CH").order_by('-date')
    national_monthlyreports = monthly_chap.filter(type="NO").order_by('-date')

    template_data["chapter_monthlyreports"] = chapter_monthlyreports
    template_data["national_monthlyreports"] = national_monthlyreports
    
    template_data['group'] = group
    template_data['is_group_admin'] = group.user_is_admin(request.user)
    template_data['is_president'] = group.user_is_president(request.user)
    
    return render_to_response('finance/monthlyreports.htm', template_data, context_instance=RequestContext(request))

@staff_member_required
def monthlyreports_dashboard(request, year=None, month=None):
#===========================================================================
# For NO. View all monthly reports and know which ones have/have not been submitted yet. 
#===========================================================================

#    
#    group = get_object_or_404(Network, slug=group_slug)
    template_data = dict()
    
    if month:
        month = int(month)
    else:
        month = datetime.date.today().month
    
    if year:
        year = int(year)
    else:
        year = datetime.date.today().year
        if month == 1:
            month = 12
            year = year - 1
        else:
            month = month - 1
            year = year

    mr_chap = MonthlyReport.objects.filter(type = "CH")
    mr_no = MonthlyReport.objects.filter(type = "NO")
    networks = Network.objects.all()
    
    table = []
    count = -1
    
#    make table of all networks and their submitted/not submitted monthly reports
    for n in networks:
        count = count + 1
        
        table.append([])
        table[count].append(n)
        
#        attach chapter monthly report
        mr = mr_chap.filter(group = n.id, date__year = year, date__month = month).order_by('-enter_date')
        if mr:
            table[count].append(mr[0])
        else:
            table[count].append("")
        
#        attach no monthly report
        mr = mr_no.filter(group = n.id, date__year = year, date__month = month).order_by('-enter_date') 
        if mr:
            table[count].append(mr[0])
        else:
            table[count].append("")
        
#    determine next/previous month/year
    if month == 1:
        template_data['prev_month'] = 12
        template_data['prev_year'] = year - 1
    else:
        template_data['prev_month'] = month - 1
        template_data['prev_year'] = year
        
    if month == 12:
        template_data['next_month'] = 1
        template_data['next_year'] = year + 1
    else:
        template_data['next_month'] = month + 1
        template_data['next_year'] = year
            
    template_data['monthly_reports'] = table
    template_data['date'] = datetime.date(year=year, month=month, day=1)
    
    return render_to_response('finance/monthlyreports_dashboard.htm', template_data, context_instance=RequestContext(request))

@group_admin_required()
def monthlyreports_id(request, id, group_slug):
#======================================================
#Monthly chapter report viewer
#======================================================
    #    get chapter
    group = get_object_or_404(Network, slug=group_slug)
    trans_chap, income_chap, donations_chap, expenditure_chap, monthly_chap = create_chapter_filters(group_slug)
    template_data = dict()
    
#    get the approporiate monthly report
#    TODO: only if the monthly report group matches group
    monthly_report = get_object_or_404(MonthlyReport, pk=id)
    mtype = monthly_report.type
    
    income_total = dict()
    income_total["total"] = 0
    expenditure_total = dict()
    expenditure_total["total"] = 0
    
    transactions = trans_chap.filter(monthlyreport = id).order_by('bank_date')
    income = income_chap.filter(monthlyreport = id)
    expenditure = expenditure_chap.filter(monthlyreport = id)
    if transactions:
        template_data['empty'] = False
        income_category = income.values('category__name').annotate(totalcategory=Sum('amount'))
        template_data["income_category"] = income_category
        income_total = income.aggregate(total = Sum('amount'))
        expenditure_category = expenditure.values('category__name').annotate(totalcategory=Sum('amount'))
        template_data["expenditure_category"] = expenditure_category
        expenditure_total = expenditure.aggregate(total = Sum('amount'))
        
        try:
            incomeChart, expenditureChart = create_category_charts(expenditure_category, income_category)
        except:
            incomeChart = None
            expenditureChart = None
    
        template_data["income_chart"] = incomeChart
        template_data["expenditure_chart"] = expenditureChart
        
    else:
        template_data['empty'] = True
      
#    find previous income/expenditures in order to find beginning start balance
#    this is a bit sketchy since it assumes reports are entered in in the right order - should be done by date 
    income_old = trans_chap.filter(monthlyreport__lt = id, monthlyreport__type = mtype, type = "IN").exclude(monthlyreport=None).aggregate(total = Sum('amount'))
    expenditure_old = trans_chap.filter(monthlyreport__lt = id, monthlyreport__type = mtype, type = "EX").exclude(monthlyreport=None).aggregate(total = Sum('amount'))
    
#    if either of the totals is None, switch to 0
    if not income_old["total"]: 
        income_old["total"] = 0
    if not expenditure_old["total"]: 
        expenditure_old["total"] = 0
    if not income_total["total"]: 
        income_total["total"] = 0
    if not expenditure_total["total"]: 
        expenditure_total["total"] = 0
        
#    determine incoming balance by using sum of all previous transactions on reports
    incoming_balance = income_old["total"] - expenditure_old["total"]

#    net for the month
    net = income_total["total"] - expenditure_total["total"]
#    outgoing balance based on incoming and net for the month
    outgoing_balance = incoming_balance + net
    
    template_data["monthly_report"] = monthly_report
    template_data["trans"] = transactions
    template_data["income_total"] = income_total
    template_data["expenditure_total"] = expenditure_total
    template_data["net"] = net
    template_data["incoming_balance"] = incoming_balance
    template_data["outgoing_balance"] = outgoing_balance

    template_data["current"] = False
    
    template_data['group'] = group
    template_data['is_group_admin'] = group.user_is_admin(request.user)
    template_data['is_president'] = group.user_is_president(request.user)
    
    return render_to_response('finance/monthlyreports_detail.htm', template_data, context_instance=RequestContext(request))

@group_admin_required()
def monthlyreports_current(request, group_slug):
#======================================================
#view current (unsubmitted) monthly report
#======================================================
    #    get chapter
    group = get_object_or_404(Network, slug=group_slug)
    trans_chap, income_chap, donations_chap, expenditure_chap, monthly_chap = create_chapter_filters(group_slug)
    template_data = dict()  
    
#    determine incoming balance 
#    use filter with type = so that it doesn't include commitments
    income_old = trans_chap.filter(monthlyreport__type = "CH", type = "IN", submitted = "Y").aggregate(total = Sum('amount'))
    expenditure_old = trans_chap.filter(monthlyreport__type = "CH", type = "EX", submitted = "Y").aggregate(total = Sum('amount'))

#    if either of the totals is None, switch to 0    
    if not income_old["total"]: 
        income_old["total"] = 0
    if not expenditure_old["total"]: 
        expenditure_old["total"] = 0
    
    incoming_balance = income_old["total"] - expenditure_old["total"]
    
#    determine earliest transaction and do report for that month
    trans = trans_chap.filter(submitted = "N", account = "CH", bank_date__isnull=False).order_by('-bank_date')
    min_transaction = trans.aggregate(min_bankdate = Min('bank_date'))
    min_date = min_transaction["min_bankdate"]
   
    if min_date:
        template_data['empty'] = False
        template_data['min_date'] = min_date
        transactions = trans.filter(bank_date__year = min_date.year, bank_date__month = min_date.month)
        income = transactions.filter(type="IN")
        expenditure = transactions.filter(type="EX")
        template_data["trans"] = transactions
        income_total = transactions.filter(type = "IN").aggregate(total = Sum('amount'))
        expenditure_total = transactions.filter(type = "EX").aggregate(total = Sum('amount'))
        #    if either of the totals is None, switch to 0    
        if not income_total["total"]: 
            income_total["total"] = 0
        if not expenditure_total["total"]: 
            expenditure_total["total"] = 0
            
        net = income_total["total"] - expenditure_total["total"]
        template_data["income_total"] = income_total
        template_data["expenditure_total"] = expenditure_total
        
#        there are transactions in the report
        if transactions:
            template_data['empty'] = False
            income_category = income.values('category__name').annotate(totalcategory=Sum('amount'))
            template_data["income_category"] = income_category
            income_total = income.aggregate(total = Sum('amount'))
            expenditure_category = expenditure.values('category__name').annotate(totalcategory=Sum('amount'))
            template_data["expenditure_category"] = expenditure_category
            expenditure_total = expenditure.aggregate(total = Sum('amount'))
            
#            create category charts
            try:
                incomeChart, expenditureChart = create_category_charts(expenditure_category, income_category)
            except:
                incomeChart = None
                expenditureChart = None
        
            template_data["income_chart"] = incomeChart
            template_data["expenditure_chart"] = expenditureChart
            
        else:
            template_data['empty'] = True
        
        transactions_category = transactions.values('category').annotate(totalcategory=Sum('amount')).order_by('category')
        template_data["trans_cat"] = transactions_category
        outgoing_balance = incoming_balance + net 
    
#    there are no transactions recorded for this month
    else:
        net = 0
        outgoing_balance = incoming_balance
        template_data['empty'] = True
#        find the last monthly report and assume one month later
        mr = monthly_chap.filter(type = "CH").aggregate(max = Max('date'))
        if mr["max"]:
#            figure out the month after the last submitted report
            if mr["max"].month == 12:
                template_data["year"] = mr["max"].year + 1
                template_data["month"]  = 1
            else:
                template_data["year"]  = mr["max"].year
                template_data["month"] = mr["max"].month + 1
            template_data['min_date'] = datetime.date(year=template_data["year"], month=template_data["month"],day=1)
#        if there haven't been any reports yet
        else:
#            one month before today
            date = datetime.date.today() - timedelta(days=30)
            template_data['min_date'] = date
            template_data["year"]  = date.year
            template_data["month"] = date.month
              
    template_data["net"] = net
    template_data["incoming_balance"] = incoming_balance
    template_data["outgoing_balance"] = outgoing_balance
    template_data["current"] = True
    
    template_data['group'] = group
    template_data['is_group_admin'] = group.user_is_admin(request.user)
    template_data['is_president'] = group.user_is_president(request.user)
    
    return render_to_response('finance/monthlyreports_detail.htm', template_data, context_instance=RequestContext(request))

@group_admin_required()
def monthlyreports_submit_confirm(request, group_slug, year=None, month=None):
    template_data = dict()
    
    template_data['empty'] = False
    if year:
        if month:
            template_data['year'] = year
            template_data['month'] = month
            template_data['empty'] = True
        else:
 #            error since not month AND year
            return HttpResponseForbidden()
        
    group = get_object_or_404(Network, slug=group_slug)
    
    template_data['group'] = group
    template_data['is_group_admin'] = group.user_is_admin(request.user)
    template_data['is_president'] = group.user_is_president(request.user)
    
    return render_to_response('finance/monthlyreports_submit_confirm.htm', template_data, context_instance=RequestContext(request))

@group_admin_required()
def monthlyreports_submit(request, group_slug, year=None, month=None):
#======================================================
#submit the most recent report
#======================================================
    #    get chapter
    group = get_object_or_404(Network, slug=group_slug)
    trans_chap, income_chap, donations_chap, expenditure_chap, monthly_chap = create_chapter_filters(group_slug)
    template_data = dict()
    
#    this is for blank reports that are submitted (the right year and date is passed in)  
    if year:
        if month:
            if (int(year)*100 + int(month)) < (datetime.datetime.now().year*100 + datetime.datetime.now().month):
    #            blank report to be submitted
                monthly_report = MonthlyReport()
                monthly_report.date=datetime.datetime(int(year),int(month), 1)
                monthly_report.group = group
                monthly_report.type = "CH"
                monthly_report.creator = request.user
                monthly_report.save()
                template_data['submitted'] = True
            else:
                template_data['submitted'] = False

        else:
#            error since not month AND year
            return HttpResponseForbidden()
            
    else:
        trans = trans_chap.filter(submitted = "N", account = "CH", bank_date__isnull=False).order_by('bank_date')
        min_transaction = trans.aggregate(min_bankdate = Min('bank_date'))
        min_date = min_transaction["min_bankdate"]
    #    TODO: message box, saying they want to submit for sure!
    #    TODO: how to edit submitted transactions... NO only?
        if (min_date.year*100 + min_date.month) < (datetime.datetime.now().year*100 + datetime.datetime.now().month):
            transactions = trans.filter(bank_date__year = min_date.year, bank_date__month = min_date.month)    
            
            mr_check = monthly_chap.filter(date__year = min_date.year, date__month = min_date.month, type = "CH")
            
            if mr_check:
                template_data['group'] = group
                return render_to_response('finance/monthlyreports_submit_error.htm', template_data, context_instance=RequestContext(request))
            
            monthly_report = MonthlyReport()
            monthly_report.date=datetime.datetime(min_date.year,min_date.month, 1)
            monthly_report.group = group
            monthly_report.type = "CH"
            monthly_report.creator = request.user
            monthly_report.save()
            
            for t in transactions:
                t.submitted = "Y"
                t.monthlyreport = monthly_report
                t.group = group
                t.creator = request.user
                if t.type == 'CM':
                    t.type = 'EX'
                t.save()
            
            template_data['submitted'] = True
        else:
            template_data['submitted'] = False
    
    template_data['group'] = group
    template_data['is_group_admin'] = group.user_is_admin(request.user)
    template_data['is_president'] = group.user_is_president(request.user)
    
    return render_to_response('finance/monthlyreports_submit.htm', template_data, context_instance=RequestContext(request))

@staff_member_required
def account_balances (request):
    
    template_data = dict()
    
    networks = Network.objects.all()
    
    table = []
    count = 0
    today = datetime.date.today()
    for n in networks:
        ch_in = Income.objects.filter(group = n.id, account = "CH", bank_date__lte=today, bank_date__isnull=False).aggregate(sum = Sum('amount'))
        ch_out = Expenditure.objects.filter(group = n.id, account = "CH", bank_date__lte=today, bank_date__isnull=False).aggregate(sum = Sum('amount'))
        no_in = Income.objects.filter(group = n.id, account = "NO", bank_date__lte=today, bank_date__isnull=False).aggregate(sum = Sum('amount'))
        no_out = Expenditure.objects.filter(group = n.id, account = "NO", bank_date__lte=today, bank_date__isnull=False).aggregate(sum = Sum('amount'))
        
        if not ch_in['sum']:
            ch_in['sum'] = 0
        if not ch_out['sum']:
            ch_out['sum'] = 0
        if not no_in['sum']:
            no_in['sum'] = 0
        if not no_out['sum']:
            no_out['sum'] = 0
            
        ch_balance = ch_in['sum'] - ch_out['sum']
        no_balance = no_in['sum'] - no_out['sum']
        net = ch_balance + no_balance
        
        if no_balance < 0:
            no_red = True
        else:
            no_red = False
        if ch_balance < 0:
            ch_red = True
        else:
            ch_red = False
        if net < 0:
            net_red = True
        else:
            net_red = False
        
        table.append([])
        table[count].append(n)
        table[count].append(ch_balance)
        table[count].append(ch_red)
        table[count].append(no_balance)
        table[count].append(no_red)
        table[count].append(net)
        table[count].append(net_red)
        count = count + 1
    
    template_data['table'] = table
    template_data['today'] = today
    

    return render_to_response('finance/accounts.htm', template_data, context_instance=RequestContext(request))

def csv_trans(request, group_slug=None, month=None, year=None):
    if group_slug:
        return csv_trans_group(request, group_slug, month, year)
    else:
        return csv_trans_staff(request, group_slug, month, year)

@group_admin_required()
def csv_trans_group(request, group_slug=None, month=None, year=None):
    return csv_trans_helper(request, group_slug, month, year)

@staff_member_required
def csv_trans_staff(request, group_slug=None, month=None, year=None):
    return csv_trans_helper(request, group_slug, month, year)

def csv_trans_helper(request, group_slug=None, month=None, year=None):
#======================================================
# csv output of all transactions
#======================================================
    
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=transactions_%d-%d-%d.csv' % (datetime.date.today().day, datetime.date.today().month, datetime.date.today().year)

    writer = csv.writer(response)
    
    #    get chapter    
    if group_slug:
        group = get_object_or_404(Network, slug=group_slug)
        trans_chap, income_chap, donations_chap, expenditure_chap, monthly_chap = create_chapter_filters(group_slug)
        row = ["Chapter", group.name]
    else:
        trans_chap = Transaction.objects.all()
        row = ["All Chapters"]
     
    writer.writerow([fix_encoding(s) for s in row])   
    
    if year:
        trans_chap = trans_chap.filter(bank_date__year=year)
        if month:
            trans_chap = trans.filter(bank_date__month=month)
            row = ["Year", year, "Month", month]
            writer.writerow([fix_encoding(s) for s in row])
        else:
            row = ["Year", year]
            writer.writerow([fix_encoding(s) for s in row])
    else:
        row = ["All transactions"]
        writer.writerow([fix_encoding(s) for s in row])
    
    row = ["Downloaded:", datetime.date.today()]
    writer.writerow([fix_encoding(s) for s in row])
    row = ["Transactions"]
    writer.writerow([fix_encoding(s) for s in row])
    row = ["Account", "Type", "Bank Date", "Category", "Description", "Amount"]
    writer.writerow([fix_encoding(s) for s in row])
    for t in trans_chap:
        row = [t.account, t.type, t.bank_date, t.category.name, t.description, t.amount]
        writer.writerow([fix_encoding(s) for s in row])
    
    return response

@group_admin_required()
def csv_monthlyreport(request, id, group_slug):
#======================================================
# csv output of monthly reports
#======================================================
    #    get chapter
    template_data = dict()
    group = get_object_or_404(Network, slug=group_slug)
    trans_chap, income_chap, donations_chap, expenditure_chap, monthly_chap = create_chapter_filters(group_slug)
    
    trans = trans_chap.filter(monthlyreport = id).order_by('bank_date')
    mr = monthly_chap.get(pk=id)
    
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=monthly_report.csv'

    writer = csv.writer(response)
    row = ["Monthly Report", mr.date.year, mr.date.month]
    writer.writerow([fix_encoding(s) for s in row])
    row = ["Account", mr.type]
    writer.writerow([fix_encoding(s) for s in row])
    row = ["Income/Expenditure", "Bank Date", "Category", "Description", "Amount"]
    writer.writerow([fix_encoding(s) for s in row])
    
    for t in trans:
        row = [t.type, t.bank_date, t.category, t.description, t.amount]
        writer.writerow([fix_encoding(s) for s in row])
        
    template_data['group'] = group
    template_data['is_group_admin'] = group.user_is_admin(request.user)
    template_data['is_president'] = group.user_is_president(request.user)
    
    return response

@staff_member_required
def csv_donationreport(request, group_slug=None):
#======================================================
# donation report
#======================================================
    #    get chapter
    if group_slug:
        group = get_object_or_404(Network, slug=group_slug)
        trans_chap, income_chap, donations_chap, expenditure_chap, monthly_chap = create_chapter_filters(group_slug)
        donations = donations_chap.order_by('bank_date')
    else:    
        donations = Donation.objects.all().order_by('bank_date')
    
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=donation_report.csv'
    writer = csv.writer(response)
    
    row = ["Donation Report"]
    writer.writerow([fix_encoding(s) for s in row])
#    TODO: make this actually look like the report
    row = ["Account", "Type", "Bank Date", "Cheque Date", "Cheque Number", "Tax Receipt Required?", "Category", "Donor", "Address", "City", "Province", "Country", "Postal Code", "Description", "Amount"]
    writer.writerow([fix_encoding(s) for s in row])
    
    for t in donations:
        row = [t.account, t.type, t.bank_date, t.cheque_date, t.cheque_num, t.taxreceipt, t.donation_category, t.donor, t.address, t.city, t.province, t.country, t.postal, t.description, t.amount]
        writer.writerow([fix_encoding(s) for s in row])
    
    return response

@staff_member_required
def csv_accountingreport(request):
#======================================================
# accounting report
#======================================================

    income = Income.objects.filter(account="CH", bank_date__isnull=False).exclude(category="Donation").order_by('group')
    donation = Donation.objects.filter(account="CH", bank_date__isnull=False).order_by('group')
    expenditure = Expenditure.objects.filter(account="CH", bank_date__isnull=False).order_by('group')
    
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=accounting_report.csv'
    writer = csv.writer(response)
    
    row = ["Accounting Report"]
    writer.writerow([fix_encoding(s) for s in row])
#    TODO: make this actually look like the report
    row = ["Chapter","Account", "Type", "Bank Date", "Category", "Description", "Amount", "Payee", "Cheque Number", "HST", "Donation Category", "Donor"]
    writer.writerow([fix_encoding(s) for s in row])
    
    for t in donation:
        row = [t.group.name, t.account, t.type, t.bank_date, t.category, t.description, t.amount, "","" ,"" ,t.donation_category, t.donor]
        writer.writerow([fix_encoding(s) for s in row])
    for t in income:
        row = [t.group.name, t.account, t.type, t.bank_date, t.category, t.description, t.amount, "","" ,"" ,"", "", ""]
        writer.writerow([fix_encoding(s) for s in row])
    for t in expenditure:
        row = [t.group.name, t.account, t.type, t.bank_date, t.category, t.description, t.amount, t.payee, t.cheque_num, t.hst, "", ""]
        writer.writerow([fix_encoding(s) for s in row])
    
    return response

@staff_member_required
def noview_commitments(request):
    template_data = dict()
    
#    income information
    commitments = Expenditure.objects.filter(type = 'CM')
    total_cm = commitments.aggregate(total=Sum('amount'))

#    if either of the totals is None, switch to 0    
    if not total_cm["total"]: 
        total_cm["total"] = 0

#    information to pass to template
    template_data["commitments"] = commitments
    template_data["total_cm"] = total_cm

    return render_to_response('finance/view_commitment.htm', template_data, context_instance=RequestContext(request))

@staff_member_required
def upload_commitments(request):
#======================================================
# upload commitments file
#======================================================

    template_data = dict()

    if request.method == 'POST':
        form = UploadCommitmentForm(request.POST, request.FILES)
        if form.is_valid(): 
#            create_noreports(request)
#            directory for file
#            directory = request.POST["dir"]

            # open file
            diskfile = tempfile.TemporaryFile(mode='w+')
            uploadedfile = request.FILES['dir']
            # write file to disk
            for chunk in uploadedfile.chunks():
                diskfile.write(chunk)

#            list of all the inputted transactions
            transactions = []
            errors = []
#            open reader to read csv file
#            reader = csv.reader(open(directory,"rb"))
            diskfile.seek(0)
            reader = csv.reader(diskfile)

            rownumber = 0
            for r in reader:
                rownumber = rownumber + 1
                print "row was read"
#                determine what type of transaction
                if r[0] == "CM":
                    try:
                        
                        c = Category.objects.get(id=r[3])
                        g = BaseGroup.objects.get(id=r[10])
                        
                        exp = Expenditure()
                        exp.type = "CM"
                        exp.bank_date = datetime.date(year=int(r[11]), month=int(r[12]), day=int(r[13]))
                        exp.amount = r[2]
#                        this is sketchy - should get the actual category
                        exp.category = c
                        exp.description = r[4]
                        exp.payee = r[5]
                        if r[8]:
                            exp.cheque_num = r[8]
                        if r[9]:
                            exp.cheque_date = r[9]
                        exp.group = g
                        exp.account = "NO"
                        exp.payee = "National Office"
                        exp.submitted = "N"
                        exp.account = "NO"
                        
                        exp.creator = request.user
                        exp.editor = request.user
                        transactions.append(exp)
                    
                        
                    except Category.DoesNotExist:
                        errors.append("Error with row " + str(rownumber) + " (" + r[4] + "), category does not exist")
                    except BaseGroup.DoesNotExist:
                        errors.append("Error with row " + str(rownumber) + " (" + r[4] + "), group does not exist")
                    except BaseGroup.DoesNotExist:
                        errors.append("Error with row " + str(rownumber) + " (" + r[4] + ")")
            
            if errors:
                for e in errors:
                 request.user.message_set.create(message="Error: " + e)
            else:
                for t in transactions:
                    t.save()
                    
            return HttpResponseRedirect(reverse('noview_commitments'))
    else:
        form = UploadCommitmentForm()
    
    template_data['form'] = form
    template_data['type'] = "commitments"
    
    return render_to_response('finance/import_commitments.htm', template_data, context_instance=RequestContext(request))

@staff_member_required
def upload_testdata(request, group_slug):
#======================================================
# upload commitments file
#======================================================
    #    get chapter
    group = get_object_or_404(Network, slug=group_slug)
    template_data = dict()
    
    if request.method == 'POST':
        form = UploadCommitmentForm(request.POST)
        if form.is_valid(): 
            directory = request.POST["dir"]    
            reader = csv.reader(open(directory,"rb"))
            for r in reader:
                if r[0] == "EX":
                    exp = Expenditure()
                    exp.type = "EX"
                    exp.bank_date = r[1]
                    exp.amount = r[2]
                    exp.category_id = r[3]
                    exp.description = r[4]
                    exp.payee = r[5]
                    exp.cheque_num = r[6]
                    exp.cheque_date = r[7]
                    exp.hst = r[8]
                    exp.group_id = r[9]
                    exp.account = "CH"
                    exp.submitted = "N"
                    exp.creator = request.user
                    exp.editor = request.user
                    exp.save()
                elif r[0] == "IN":
                    income = Income()
                    income.type = "IN"
                    income.bank_date = r[1]
                    income.amount = r[2]
                    income.category_id = r[3]
                    income.description = r[4]
                    income.group_id = r[9]
                    income.account = "CH"
                    income.submitted = "N"
                    income.creator = request.user
                    income.editor = request.user
                    income.save()
                elif r[0] == "CM":  
                    print "commitment"
                else:
                    print "title"
#            return HttpResponseRedirect('upload_file')
    else:
        form = UploadCommitmentForm()
    
    template_data['group'] = group
    template_data['is_group_admin'] = group.user_is_admin(request.user)
    template_data['is_president'] = group.user_is_president(request.user)
    template_data['form'] = form
    template_data['type'] = "testdata"
    
    return render_to_response('finance/import.htm', template_data, context_instance=RequestContext(request))

def submit_notransaction(transaction):
 #==============================================================================
 # helper function to submit a specific transaction to an NO monthly report      
 #==============================================================================
    mr = MonthlyReport.objects.filter(type="NO")
#        find monthly report by chapter, month, year 
    tdate = transaction.bank_date
    mr = mr.filter(group=transaction.group, date__month=tdate.month, date__year=tdate.year)
    for m in mr:
#            associate the transaction with that monthly report
        transaction.monthlyreport = m
        transaction.submitted = "Y"
        transaction.save()
    
    return True

@staff_member_required
def create_noreports(request):
#===============================================================================
# helper function to create all the NO monthly reports
#===============================================================================
    networks = Network.objects.all()
    mr = MonthlyReport.objects.filter(type="NO")
    date = request.POST["month"]
    for n in networks:                
#                check to make sure that the report isn't already made
        mr_chap = mr.filter(group=n)
        flag = True
        for m in mr_chap:
#           TODO: figure out how to make this comparison (unicode to datetime)
            if str(date) == str(m.date):
                flag = False
                   
#       make new report
        if flag:
            m = MonthlyReport()
            m.group = n
            m.type = "NO"
            m.date = date
            m.creator = request.user
            m.save()
    return

@staff_member_required
def upload_noreport(request):
#======================================================
# upload NO report from quickbooks output
#======================================================
    #    get chapter
    template_data = dict()

    if request.method == 'POST':
        form = UploadCommitmentForm(request.POST, request.FILES)
        if form.is_valid(): 
            create_noreports(request)
#            directory for file
#            directory = request.POST["dir"]

            # open file
            diskfile = tempfile.TemporaryFile(mode='w+')
            uploadedfile = request.FILES['dir']
            # write file to disk
            for chunk in uploadedfile.chunks():
                diskfile.write(chunk)

#            list of all the inputted transactions
            transactions = []
            errors = []
#            open reader to read csv file
#            reader = csv.reader(open(directory,"rb"))
            diskfile.seek(0)
            reader = csv.reader(diskfile)

            rownumber = 0
            for r in reader:
                rownumber = rownumber + 1
                print "row was read"
#                determine what type of transaction
                if r[0] == "EX":
                    try:
                        c = Category.objects.get(id=r[3])
                        g = BaseGroup.objects.get(id=r[10])

                        exp = Expenditure()
                        exp.type = "EX"
                        exp.bank_date = datetime.date(year=int(r[11]), month=int(r[12]), day=int(r[13]))
                        exp.amount = r[2]
#                        this is sketchy - should get the actual category
                        exp.category = c
                        exp.description = r[4]
                        exp.payee = r[5]
                        if r[8]:
                            exp.cheque_num = r[8]
                        if r[9]:
                            exp.cheque_date = r[9]
                        exp.group = g
                        exp.account = "NO"
                        exp.submitted = "N"
                        exp.creator = request.user
                        exp.editor = request.user
                        #exp.save()
                        transactions.append(exp)
                        #submit_notransaction(exp)
                    except Category.DoesNotExist:
                        errors.append("Error with row " + str(rownumber) + " (" + r[4] + "), category does not exist")
                    except BaseGroup.DoesNotExist:
                        errors.append("Error with row " + str(rownumber) + " (" + r[4] + "), group does not exist")
                    except:
                        errors.append("Error with row " + str(rownumber) + " (" + r[4] + ")")
                
                elif r[0] == "IN":
                    try:
                        c = Category.objects.get(id=r[3])
                        g = BaseGroup.objects.get(id=r[10])

                        income = Income()
                        income.type = "IN"
                        income.bank_date = datetime.date(year=int(r[11]), month=int(r[12]), day=int(r[13]))
                        income.amount = r[2]
#                        this is sketchy - should get the actual category
                        income.category = c
                        income.description = r[4]
                        income.group = g
                        income.account = "NO"
                        income.submitted = "N"
                        income.creator = request.user
                        income.editor = request.user
                        #income.save()
                        transactions.append(income)
                        #current = income
                        #submit_notransaction(income)
                    except Category.DoesNotExist:
                        errors.append("Error with row " + str(rownumber) + " (" + r[4] + "), category does not exist")
                    except BaseGroup.DoesNotExist:
                        errors.append("Error with row " + str(rownumber) + " (" + r[4] + "), group does not exist")
                    except BaseGroup.DoesNotExist:
                        errors.append("Error with row " + str(rownumber) + " (" + r[4] + ")")
                elif r[0] == "DN":
                    try:
                        c = Category.objects.get(id=r[3])
                        g = BaseGroup.objects.get(id=r[10])

                        donation = Donation()
                        donation.type = "IN"
                        donation.bank_date = datetime.date(year=int(r[11]), month=int(r[12]), day=int(r[13]))
                        donation.amount = r[2]
#                        this is sketchy - should get the actual category
                        donation.category = c
                        donation.description = r[4]
                        donation.donor = r[5]
                        donation.donation_category = r[6]
                        donation.address = r[7]
                        if r[8]:
                            exp.cheque_num = r[8]
                        if r[9]:
                            exp.cheque_date = r[9]
                        donation.group = g
                        donation.account = "NO"
                        donation.submitted = "N"
                        donation.creator = request.user
                        donation.editor = request.user
                        #donation.save()
                        transactions.append(donation)
                        #current = donation
                        #submit_notransaction(donation)
                    except Category.DoesNotExist:
                        errors.append("Error with row " + str(rownumber) + " (" + r[4] + "), category does not exist")
                    except BaseGroup.DoesNotExist:
                        errors.append("Error with row " + str(rownumber) + " (" + r[4] + "), group does not exist")
                    except BaseGroup.DoesNotExist:
                        errors.append("Error with row " + str(rownumber) + " (" + r[4] + ")")

            if errors:
                for e in errors:
                 request.user.message_set.create(message="Error: " + e)
            else:
                for t in transactions:
                    t.save()
                    submit_notransaction(t)
            return HttpResponseRedirect(reverse('view_allnoreports'))
    else:
        form = UploadCommitmentForm()
    
    template_data['form'] = form
    
    return render_to_response('finance/import_noreports.htm', template_data, context_instance=RequestContext(request))



#===============================================================================
# def create_noreport(request):
#    template_data = dict()
# 
#    networks = Network.objects.all()
#    mr = MonthlyReport.objects.filter(type="NO")
#    
#    if request.method == 'POST':
#        form = CreateNOReports(request.POST)
#        if form.is_valid():       
#            date = request.POST['month']
#            for n in networks:                
# #                check to make sure that the report isn't already made
#                mr = mr.filter(group=n)
#                flag = True
#                for m in mr:
#                    test = m.date
# #                    TODO: figure out how to make this comparison (unicode to datetime)
#                    if m.date == date:
#                        flag = False
#                    
# #                make new report
#                if flag:
#                    m = MonthlyReport()
#                    m.group = n
#                    m.type = "NO"
#                    m.date = date
#                    m.creator = request.user
#                    m.save()
#                
#            return HttpResponseRedirect(reverse('view_allnoreports')) # Redirect after POST   
#    else:
#        form = CreateNOReports()
#    
#    template_data['form'] = form
#    
#    return render_to_response('finance/create_noreports.htm', template_data, context_instance=RequestContext(request))
#===============================================================================
@staff_member_required
def view_allnoreports(request):
    template_data = dict()
    mr = MonthlyReport.objects.filter(type="NO").order_by('group')
    
    template_data['national_monthlyreports'] = mr
    
    return render_to_response('finance/view_allnoreports.htm', template_data, context_instance=RequestContext(request))

@staff_member_required
def upload_file(request, group_slug):
    template_data = dict()
    #    get chapter
    group = get_object_or_404(Network, slug=group_slug)
    
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid(): 
            print "testing"          
 #            handle_uploaded_file(request.FILES['file'])
#            handle_uploaded_file()
 #            return HttpResponseRedirect('upload_file')
    else:
        form = UploadFileForm()
    
    template_data['group'] = group
    template_data['is_group_admin'] = group.user_is_admin(request.user)
    template_data['is_president'] = group.user_is_president(request.user)
    
    return render_to_response('finance/import.htm', {'form': form})

@group_admin_required()
def budgets(request, group_slug):
    template_data = dict()
    group = get_object_or_404(Network, slug=group_slug)
    budgets = Budget.objects.filter(group__slug=group_slug).order_by('-start_date')
    
    template_data['budgets'] = budgets
    template_data['group'] = group
    template_data['is_group_admin'] = group.user_is_admin(request.user)
    template_data['is_president'] = group.user_is_president(request.user)
    
    return render_to_response('finance/budgets.htm', template_data, context_instance=RequestContext(request))

@group_admin_required()
def input_budgetitems(request, group_slug, budget):
    group = get_object_or_404(Network, slug=group_slug)
    budget = get_object_or_404(Budget, pk=budget)
    template_data = dict()
    trans_chap, income_chap, donations_chap, expenditure_chap, monthly_chap = create_chapter_filters(group_slug)

#    determine number of categories
    categories = Category.objects.all()
    
#    count_cat = Category.objects.aggregate(count = Count('id'))
#    count = count_cat['count']
    count_cat = categories.count()
    
#    make number of forms for number of categories
    budgetFormSet = formset_factory(BudgetItemForm, extra=count_cat)
    
#    this timeframe a year ago?
    start = budget.start_date - timedelta(days=365)
    end = budget.end_date - timedelta(days=365)
    trans = trans_chap.filter(bank_date__range=(start, end)).values('category').annotate(sum = Sum('amount'))
    
    if request.method == 'POST':
        formset = budgetFormSet(request.POST)
        if formset.is_valid():
            count = 0
            for form in formset.forms:
                f = request.POST["form-%s-amount" % count]
                item = BudgetItem()
                item.amount = f
                item.type = categories[count].type
                item.category = categories[count]
                item.budget = budget
                item.save()
                count = count + 1
            
            return HttpResponseRedirect(reverse('view_budget', kwargs={'group_slug': group.slug, 'budget': budget.id}) )
        
    else:
        formset = budgetFormSet()
        income = []
        expenditure = []
        count = 0
        
#        this is all so it outputs nicely
        for form in formset.forms:
#            separate the income from expenditure categories
            if categories[count].type == "IN":
                if trans:
                    for t in trans:
                        if t['category'] == i.category_id:
#                            set table to category name, budgeted amount, previous years' amount
                            income.append((categories[count].name, form, t['sum']))
                        else:
                            income.append((categories[count].name, form, 0))
                else:
                    income.append((categories[count].name, form, 0))
                        
            else:
                if trans:
                    for t in trans:
                        if t['category'] == i.category_id:
                            expenditure.append((categories[count].name, form, t['sum']))
                        else:
                            expenditure.append((categories[count].name, form, 0))
                else:
                    expenditure.append((categories[count].name, form, 0))

            count = count + 1
            
        template_data['income'] = income
        template_data['expenditure'] = expenditure

    template_data['formset'] = formset
    template_data['budget'] = budget
    template_data['group'] = group
    template_data['is_group_admin'] = group.user_is_admin(request.user)
    template_data['is_president'] = group.user_is_president(request.user)
    
    return render_to_response('finance/input_budget.htm', template_data, context_instance=RequestContext(request))

@group_admin_required()
def view_budget(request, group_slug, budget):
    group = get_object_or_404(Network, slug=group_slug)
    budget_object = get_object_or_404(Budget, pk=budget)
    template_data = dict()
    trans_chap, income_chap, donations_chap, expenditure_chap, monthly_chap = create_chapter_filters(group_slug)
    
    
    items = BudgetItem.objects.filter(budget=budget_object)
    if items:
        template_data['budget_items'] = items
        template_data['empty'] = False
        
        trans = trans_chap.filter(bank_date__range=(budget_object.start_date, budget_object.end_date)).values('category').annotate(sum = Sum('amount'))
        total_income = income_chap.filter(bank_date__range=(budget_object.start_date, budget_object.end_date)).aggregate(sum = Sum('amount'))
        total_expenditure = expenditure_chap.filter(bank_date__range=(budget_object.start_date, budget_object.end_date)).aggregate(sum = Sum('amount'))
        
#        if either are None, set to 0
        if not total_expenditure['sum']:
            total_expenditure['sum'] = 0
        if not total_income['sum']:
            total_income['sum'] = 0 
        
        template_data['net'] = total_income['sum'] - total_expenditure['sum']
            
                
        income = []
        expenditure = []
        count = 0
        flag = True
        total_budgetincome = 0
        total_budgetexpenditure = 0
        
#        make table for budgeted versus actual
        for i in items:
            for t in trans:
                if t['category'] == i.category_id:
#                    determine if the text should be red (under budgeted for income categories, over budgeted for expenditure categories)
                    if i.type == "IN":
                        if t['sum'] < i.amount:
                            red = True
                        else:
                            red = False
                        income.append((i, t['sum'],red))
                        total_budgetincome = total_budgetincome + i.amount
                        flag = False
                    else:
                        if t['sum'] > i.amount:
                            red = True
                        else:
                            red = False
                        expenditure.append((i, t['sum'],red))
                        total_budgetexpenditure = total_budgetexpenditure + i.amount
                        flag = False
#            if it gets here, then there are no transactions in that category yet
            if flag:
                if i.type == "IN":
                    red = True
                    income.append((i, float(0), red))
                    total_budgetincome = total_budgetincome + i.amount
                else:
                    red = False
                    expenditure.append((i, float(0), red))
                    total_budgetexpenditure = total_budgetexpenditure + i.amount
            flag = True
        
        template_data['total_income'] = total_income['sum']
        template_data['total_expenditure'] = total_expenditure['sum']
        
        template_data['total_budgetincome'] = total_budgetincome
        template_data['total_budgetexpenditure'] = total_budgetexpenditure
        template_data['net_budget'] = total_budgetincome - total_budgetexpenditure
        template_data['expenditure'] = expenditure
        template_data['income'] = income             
    else:
        template_data['empty'] = True
        
    
    template_data['budget'] = budget_object
    template_data['group'] = group
    template_data['is_group_admin'] = group.user_is_admin(request.user)
    template_data['is_president'] = group.user_is_president(request.user)   
    
    return render_to_response('finance/view_budget.htm', template_data, context_instance=RequestContext(request))

@group_admin_required()
def create_budget (request, group_slug):
    group = get_object_or_404(Network, slug=group_slug)
    
    template_data = dict()
    
    if request.method == 'POST': # If the form has been submitted...
        form = BudgetForm(request.POST) # A form bound to the POST data

        #validate fields
        if form.is_valid(): # check if fields validated
                cleaned_data = form.cleaned_data
                # Process the data in form.cleaned_data
                budget = form.save(commit=False)
                budget.group = group
                budget.creator = request.user
                budget.edited_by = request.user
                budget.save()
                
                return HttpResponseRedirect(reverse('view_budget', kwargs={'group_slug': group.slug, 'budget': budget.id}) ) # Redirect after POST
    else:
        form = BudgetForm() # A blank unbound form
    
    template_data["form"] = form #pass the form to template as "form" variable    
    template_data['group'] = group
    template_data['is_group_admin'] = group.user_is_admin(request.user)
    template_data['is_president'] = group.user_is_president(request.user)
    
    return render_to_response('finance/create_budget.htm', template_data, context_instance=RequestContext(request))

@staff_member_required
def no_budgets(request):
    template_data = dict()
    budgets = Budget.objects.all().order_by('group')
    
    template_data['budgets'] = budgets
    
    return render_to_response('finance/no_budgets.htm', template_data, context_instance=RequestContext(request))   
