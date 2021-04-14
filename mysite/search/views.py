from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import ListView
from django_tables2.config import RequestConfig
from datetime import datetime, timedelta

from .models import Files
from .forms import SearchForm
from .tables import FilesTable

def results(request):
    if request.method == 'POST':
        #check cookie from previous view
        #if request.session.test_cookie_worked():
        #    request.session.delete_test_cookie()
        #else:
        #    return HttpResponse("Please enable cookies and try again.")

        # Create a form instance and populate it with data from the request (binding):
        form = SearchForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            #process the data in form.cleaned_data as required 
            pattern = form.cleaned_data['pattern']
            case_sensitive = form.cleaned_data['case_sensitive'] #not used
            #instead: if a value is set, then use it as an option for the query. if not set, dont run it (-> not just with a big default maximum or minimum)
            if form.cleaned_data['min_size']:
                min_size = int(form.cleaned_data['min_size'])
            else:
                min_size = 0

            if form.cleaned_data['max_size']:
                max_size = int(form.cleaned_data['max_size'])
            else:
                max_size = 9223372036854775807
                        
            if form.cleaned_data['min_age']:
                min_age = int(form.cleaned_data['min_age'])
            else:
                min_age = 0

            #if notform.cleaned_data['max_age']: isn't true when max_age = 0?
            if not form.cleaned_data['max_age'] == None:
                max_age = int(form.cleaned_data['max_age'])
            else:
                max_age = 200000           
            
            request.session['pattern'] = pattern
            request.session['min_size'] = min_size
            request.session['max_size'] = max_size
            request.session['case_sensitive'] = case_sensitive
            request.session['min_age'] = min_age
            request.session['max_age'] = max_age
    #if GET
    else:
        #get the form data from the session
        try:
            pattern = request.session['pattern']
            min_size = request.session['min_size']
            max_size = request.session['max_size']
            case_sensitive = request.session['case_sensitive']
            min_age = request.session['min_age']
            max_age = request.session['max_age']
        except KeyError:
            return HttpResponse('Please enable cookies.')

    data = Files.objects.filter(filefullpath__icontains=pattern, filesize__gte=min_size, filesize__lte=max_size)
    min_date = datetime.today() - timedelta(days=min_age)
    data = data.exclude(filelastmodificationdate__gt=min_date)
    #Bug: when max_age = 0, all entries are shown
    # when 0 is entered, somehow the max_value is taken
    max_date = datetime.today() - timedelta(days=int(max_age))
    data = data.exclude(filelastmodificationdate__lt=max_date)
    table = FilesTable(data)    
    RequestConfig(request, paginate={'per_page': 25}).configure(table)
    return render(request, 'search/results.html', {'table': table })

def search(request):
    #request.session.set_test_cookie()
    form = SearchForm()

    context = {
        'form': form,
    }

    return render(request, 'search/search.html', context)
    


