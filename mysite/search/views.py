from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import ListView
from django.core import serializers
#from django.utils.cache import patch_cache_control
from django.db.models import Count, Sum
from django_tables2.config import RequestConfig
from datetime import datetime, timedelta
import matplotlib
matplotlib.use('AGG')
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import base64
from io import BytesIO
import numpy as np
import hashlib

from .models import Files
from .forms import SearchForm
from .tables import FilesTable

def y_fmt_thousand(x, y):
    return '%1.0fk' % (x / 1000)

def get_chart():
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    chart = base64.b64encode(buffer.getvalue())
    chart = chart.decode('utf-8')
    buffer.close()
    return chart

#how to do without pyplot because not recommended? https://matplotlib.org/stable/gallery/user_interfaces/web_application_server_sgskip.html#sphx-glr-gallery-user-interfaces-web-application-server-sgskip-py
#doesnt group e.g. yml and yaml together, also is case sensitive
def get_plot_extension_count(query_res, size):
    #only file extensions occuring more often than 1% of all files are shown
    total = query_res.count()
    min_count =  total * 0.01
    #group by file extension and count
    extensions = query_res.values_list('fileextension').annotate(c=Count('fileextension')).filter(c__gte=min_count).order_by('c')
    extensions_count = 0 #number of all files that are listed to calculate the "other" extensions pie size
    for element in extensions:
        extensions_count += element[1]

    extension_names = [x[0] for x in extensions]    
    extension_counts = [x[1] for x in extensions]
    
    if total > extensions_count:
        extension_names.append("Other")
        extension_counts.append(total - extensions_count) #number of "other" filetypes that are too few to have their own listing
    fig, ax = plt.subplots(figsize=size)
    cmap = plt.cm.get_cmap('Blues', len(extension_counts))
    ax.pie(extension_counts, labels=extension_names, colors=cmap(np.linspace(0.0, 1, len(extension_counts))))
    ax.axis('equal')
    
    plt.title('File extensions by number of files')
    return get_chart()  

#doesnt group e.g. yml and yaml together, also is case sensitive
def get_plot_extension_size(query_res, size):
    data = query_res.values_list('fileextension').annotate(size=Sum('filesize')).order_by('-size')
    amount_to_plot = 19 #0-index    
    extensions = [x[0] for x in data[:amount_to_plot]]
    sizes = [x[1] for x in data[:amount_to_plot]]
    if len(data) > amount_to_plot + 1:
        other_size = 0
        for element in data[amount_to_plot:]:
            other_size += element[1]
        extensions.insert(0, "Other")
        sizes.insert(0, other_size)

    fig, ax = plt.subplots(figsize=size)
    cmap = plt.cm.get_cmap('Blues', len(sizes))
    ax.pie(sizes, labels=extensions, colors=cmap(np.linspace(0.0, 1, len(sizes))))
    ax.axis('equal')
    plt.title('File extensions by file size')
    return get_chart()  

def get_plot_size(query_res, size):
    data = query_res.values_list('filesize')
    sizes = [x[0] for x in data]
    fig, ax = plt.subplots(figsize=size)

    #freedman-diaconis rule
    #q25, q75 = np.percentile(sizes,[.25,.75])
    #bin_width = 2*(q75 - q25)*len(sizes)**(-1/3)
    #bins = round((sizes.max() - sizes.min())/bin_width)

    ax.hist(sizes, bins=20, density=True) #, log=True
    plt.xlabel('File size')
    plt.title('File size distribution')
    return get_chart()

#plot showing number of files for each year over the past 5 years
def get_plot_time(query_res, size):
    years_shown = 5
    year = datetime.now().year
    other = query_res.filter(filelastmodificationdate__lt=year - years_shown).count()
    x = list() #years
    y = list() #count
    #do this with a proper query instead?
    for i in range(years_shown):
        x.append(str(year))
        y.append(query_res.filter(filelastmodificationdate__gte=year, filelastmodificationdate__lt=year + 1).count())
        year -= 1
    
    x.append("Other")
    y.append(other)
    fig, ax = plt.subplots(figsize=size)
    ax.bar(x, y)
    plt.title('Number of files modified per year')
    plt.xlabel('Year')
    plt.ylabel('Number of files')
    plt.gca().invert_xaxis()
    if max(y) > 10000:
        formatter = FuncFormatter(y_fmt_thousand)
        ax.yaxis.set_major_formatter(formatter)
    return get_chart()

def get_plot_owner(query_res, size):
    data = query_res.values_list('fileowner').annotate(c=Count('fileowner'))
    fig, ax = plt.subplots(figsize=size)
    x = [x[0] for x in data]
    y = [x[1] for x in data]
    ax.bar(x, y) #log=True
    plt.title('Number of files by owner')
    plt.xlabel('User ID')
    plt.ylabel('Number of files') 
    if max(y) > 10000:
        formatter = FuncFormatter(y_fmt_thousand)
        ax.yaxis.set_major_formatter(formatter)  
    return get_chart()

def get_hash(query_strings):
    #argument is a tuple
    string = ""
    for s in query_strings:
        string += s
    return hashlib.md5(string.encode()).hexdigest()

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
    max_date = datetime.today() - timedelta(days=int(max_age))
    data = data.exclude(filelastmodificationdate__lt=max_date)
    table = FilesTable(data) 
    RequestConfig(request, paginate={'per_page': 25}).configure(table)
    data = data.exclude(filetype__contains='dir')
    chart_size = (12.8, 9.6)
    #return HttpResponse(get_plot_extension_size(data, chart_size))
    context = {
        'table': table,
        'chart_extension_count': get_plot_extension_count(data, chart_size),
        'chart_size': get_plot_size(data, chart_size),
        'chart_time': get_plot_time(data, chart_size),
        'chart_owner': get_plot_owner(data, chart_size),
        'chart_extension_size': get_plot_extension_size(data, chart_size),
    }
    # response = render(request, 'search/results.html', context)
    # patch_cache_control(response, private=True, max_age=43200)
    # return response
    return render(request, 'search/results.html', context)   

def search(request):
    form = SearchForm()

    context = {
        'form': form,
    }

    return render(request, 'search/search.html', context)
    


