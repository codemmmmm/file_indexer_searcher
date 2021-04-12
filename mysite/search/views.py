from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import ListView
from django_tables2.config import RequestConfig

from .models import Files
from .forms import SearchForm
from .tables import FilesTable

def results(request):
    if request.method == 'POST':        
        # Create a form instance and populate it with data from the request (binding):
        form = SearchForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            #process the data in form.cleaned_data as required 
            pattern = form.cleaned_data['pattern']
            min_size = int(form.cleaned_data['min_size'])
            max_size = int(form.cleaned_data['max_size'])
            case_sensitive = form.cleaned_data['case_sensitive'] #not used
            # context = {
            #     'entries': 
            # }

            table = FilesTable(Files.objects.filter(filefullpath__icontains=pattern, filesize__gte=min_size, filesize__lte=max_size))
            
            #return HttpResponseRedirect(reverse('index')) #HttpResponseRedirect(reverse('search/index'))
    else:
        table = FilesTable(Files.objects.all())

    RequestConfig(request, paginate={"per_page": 25}).configure(table)
    return render(request, 'search/results.html', {"table": table })

    # template = loader.get_template('search/index.html')
    # context = {
    #     'filtered_entries': Files.objects.all()[:5],
    # }
    # return HttpResponse(template.render(context, request))

def search(request):
    # If this is a POST request then process the Form data
    if request.method == 'POST':        
        # Create a form instance and populate it with data from the request (binding):
        form = SearchForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            #process the data in form.cleaned_data as required 
            pattern = form.cleaned_data['pattern']
            min_size = int(form.cleaned_data['min_size'])
            max_size = int(form.cleaned_data['max_size'])
            case_sensitive = form.cleaned_data['case_sensitive'] #not used
            # context = {
            #     'entries': 
            # }

            table = FilesTable(Files.objects.filter(filefullpath__icontains=pattern, filesize__gte=min_size, filesize__lte=max_size))

            #redirect to a new URL:
            return render(request, 'search/results.html', {"table": table })
            #return HttpResponseRedirect(reverse('index')) #HttpResponseRedirect(reverse('search/index'))

    # If this is a GET (or any other method) create the default form.
    else:
        form = SearchForm()

    context = {
        'form': form,
    }

    return render(request, 'search/search.html', context)
    


