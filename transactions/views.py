# Create your views here.

#import Django stuff
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.db.models import Avg, Max, Min, Count, Sum

#import models
from transactions.models import Transaction, Income, Expenditure, IncomeCategory, ExpenditureCategory
from transactions.models import ExpenditureForm, IncomeForm



def index(request):
#================================================================================
# index
#================================================================================
    template = dict()
    
    return render_to_response('transactions/index.htm',template, context_instance=RequestContext(request))


def create_income(request):
#================================================================================
# create income object
#================================================================================
    #dictionary that passes information to the template
    template = dict()
    
    # If the form has been submitted
    if request.method == 'POST': 
        form = IncomeForm(request.POST)

        #validate fields
        if form.is_valid(): # check if fields validated
            cleaned_data = form.cleaned_data
            form.save()
            return HttpResponseRedirect(reverse('index'))
            
    #else blank form   
    else:
        form = IncomeForm()

    template['form'] = form
    
    #tells the view which template to use, and to pass the template dictionary
    return render_to_response('transactions/create_income.htm',template, context_instance=RequestContext(request))

def create_expenditure(request):
#================================================================================
# create expenditure object
#================================================================================
    template = dict()
    
    # If the form has been submitted
    if request.method == 'POST': 
        form = ExpenditureForm(request.POST)

        #validate fields
        if form.is_valid(): # check if fields validated
            cleaned_data = form.cleaned_data
            form.save()
            return HttpResponseRedirect(reverse('index'))
        
    
    #else blank form   
    else:
        form = ExpenditureForm()

    template['form'] = form
    
    return render_to_response('transactions/create_expenditure.htm',template, context_instance=RequestContext(request))

def view_all(request):
#================================================================================
# view all transactions
#================================================================================
    template = dict()
    
    #get all the transactions
    expenditures = Expenditure.objects.all()
    incomes = Income.objects.all()
    
    #save variables to be passed into the template for use there
    template['expenditures'] = expenditures
    template['incomes'] = incomes
    template['ugh'] = "this is sooo frustrating"
    
    
    return render_to_response('transactions/view_all.htm',template, context_instance=RequestContext(request))