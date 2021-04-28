from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import ListView
from django.core import serializers
from django.db.models import Count
from django_tables2.config import RequestConfig
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import base64
from io import BytesIO

from .models import Files
from .forms import SearchForm
from .tables import FilesTable

# def get_chart():
#     buffer = BytesIO()
#     plt.savefig(buffer, format='png')
#     buffer.seek(0)
#     image = buffer.getvalue()
#     chart = base64.b64encode(image)
#     chart = chart.decode('utf-8')
#     buffer.close()
#     return chart

#how to do without pyplot?
def get_plot():
    #only file extensions occuring more often than 1% of all files are shown
    total = Files.objects.count()
    min_count =  total * 0.01
    #group by file extension and count, exclude empty extension, take only
    extensions = Files.objects.values_list('fileextension').annotate(c=Count('fileextension')).filter(c__gte=min_count).order_by('c').exclude(fileextension="")
    extensions_count = 0 #number of all files that are listed to calculate the "other" extensions pie size
    for element in extensions:
        extensions_count += element[1]
    extension_names = [x[0] for x in extensions]
    extension_names.append("Other")
    extension_counts = [x[1] for x in extensions]
    extension_counts.append(total - extensions_count) #number of "other" filetypes that are too few to have their own listing
    
    fig, ax = plt.subplots()
    ax.pie(extension_counts, labels=extension_names)
    ax.axis('equal')
    buffer = BytesIO()
    fig.savefig(buffer)
    chart = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return chart
    #plt.savefig("x")

def results(request):
    if request.method == 'POST':
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

            data_format = form.cleaned_data['data_format']
            
            request.session['pattern'] = pattern
            request.session['min_size'] = min_size
            request.session['max_size'] = max_size
            request.session['case_sensitive'] = case_sensitive
            request.session['min_age'] = min_age
            request.session['max_age'] = max_age
            request.session['data_format'] = data_format
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
            data_format = request.session['data_format']
        except KeyError:
            return HttpResponse('Please enable cookies.')

    #if data_format == 'json':
    #    json = serializers.serialize('json', Files.objects.all())

    data = Files.objects.filter(filefullpath__icontains=pattern, filesize__gte=min_size, filesize__lte=max_size)
    min_date = datetime.today() - timedelta(days=min_age)
    data = data.exclude(filelastmodificationdate__gt=min_date)
    max_date = datetime.today() - timedelta(days=int(max_age))
    data = data.exclude(filelastmodificationdate__lt=max_date)
    table = FilesTable(data)    

    

    RequestConfig(request, paginate={'per_page': 25}).configure(table)
    return render(request, 'search/results.html', {'table': table, 'chart': get_plot() })

def search(request):
    form = SearchForm()

    context = {
        'form': form,
    }

    return render(request, 'search/search.html', context)
    


