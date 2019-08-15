from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET
from django.http import HttpResponse
from django.template import loader
from django.conf import settings
from django.views.generic import TemplateView
from . import models
from . import dt


# Create your views here.
def home(request):
    return render(request, 'home.html')


@login_required
def my(request):
    query_results = models.Batchs.objects.filter(User_ID=request.user).order_by('-Batch_Received_DateTime')

    template = loader.get_template('my.html')

    context = {
        'query_results': query_results,
    }

    return HttpResponse(template.render(context, request))


# no login
def public(request):
    from . import models

    public_batches = models.Batchs.objects.filter(Project_IsPublic=True).order_by('-Batch_Received_DateTime')

    template = loader.get_template('public.html')

    context = {
        'public_batches': public_batches,
    }

    return HttpResponse(template.render(context, request))


@login_required
def send(request):
    from django.http import HttpResponseRedirect

    return HttpResponseRedirect('/send1')


@login_required
def send1(request):
    from django.http import HttpResponseRedirect, Http404
    from . import forms
    from . import helpers

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        form = forms.SendForm1(request.POST, request.FILES)

        if form.is_valid():
            batch = form.save(commit=False)
            batch.User_ID = request.user
            batch.save()

            # analyse
            uploaded = batch.Project_FileSourcePathName.path
            helpers.handle_uploaded_file(uploaded, batch, batch.Batch_Id)
            batch.save()

            return HttpResponseRedirect('/send2/{}'.format(batch.Batch_Id))

    # if a GET (or any other method) we'll create a blank form
    else:
        form = forms.SendForm1()

    return render(request, 'send1.html', {'form': form})


@login_required
def send2(request, batch_id):
    from django.http import HttpResponseRedirect, Http404
    from . import forms
    from . import models

    # check access
    batch = models.Batchs.objects.get(Batch_Id=batch_id)

    if batch.User_ID == request.user:
        pass
    else:
        raise Http404

    # POST
    if request.method == 'POST':
        form = forms.SendForm2(request.POST, request.FILES, instance=batch)

        if form.is_valid():
            form.save()

            if 'btn_next' in request.POST:
                return HttpResponseRedirect('/send3/{}'.format(batch.Batch_Id))

    # GET
    else:
        form = forms.SendForm2(instance=batch)

    # render
    titles = models.BatchInput(batch.Batch_Id).get_column_names(without_pk=True)

    desc_fields   = list(form.get_desc_fields())
    inout_fields  = list(form.get_inout_fields())
    errors        = [batch.AnalysisSource_Errors.get(t, "") for t in titles]
    error_dataset = batch.AnalysisSource_Errors.get("DATASET", "")
    warnings      = [batch.AnalysisSource_Warnings.get(t, "") for t in titles]
    types         = [batch.AnalysisSource_ColumnType.get(t, "") for t in titles]

    l = len(titles)

    desc_fields   = desc_fields[0:l]
    inout_fields  = inout_fields[0:l]
    errors        = errors[0:l]
    error_dataset = error_dataset
    warnings      = warnings[0:l]
    types         = types[0:l]

    # table name -> model name
    # columns -> c0, c1, c2, ....
    #   CharField()
    #   IntegerField()

    template = loader.get_template('send2.html')

    context = {
        'form': form,
        'batch': batch,
        'titles': titles,
        'desc_fields': desc_fields,
        'inout_fields': inout_fields,
        'has_errors': any(errors),
        'errors': errors,
        'error_dataset': error_dataset,
        'has_warnings': any(warnings),
        'warnings': warnings,
        'types': types,
    }

    return HttpResponse(template.render(context, request))


@login_required
def send3(request, batch_id):
    from django.http import HttpResponseRedirect, Http404
    from . import forms
    from . import helpers

    # check access
    batch = models.Batchs.objects.get(Batch_Id=batch_id)

    if batch.User_ID == request.user:
        pass
    else:
        raise Http404

    # POST
    if request.method == 'POST':
        form = forms.SendForm3(request.POST, request.FILES, instance=batch)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/send3/{}'.format(batch.Batch_Id))

    # GET
    else:
        form    = forms.SendForm3(instance=batch)

    # render
    template = loader.get_template('send3.html')
    context = {
        'form': form,
        'batch': batch,
    }
    return HttpResponse(template.render(context, request))


#@login_required
def view(request, batch_id):
    import os
    import json
    from django.http import Http404
    from django.conf import settings
    from . import models
    from . import helpers

    FIRST_LINES = 5
    LAST_LINES = 5

    # check access
    batch = models.Batchs.objects.get(Batch_Id=batch_id)

    if batch.Project_IsPublic:
        pass
    else:
        if batch.User_ID == request.user:
            pass
        else:
            raise Http404

    # query lines
    data_titles = models.BatchInput(batch_id).get_column_names(without_pk=True)
    data_head = models.BatchInput.get_head(batch_id, FIRST_LINES)
    data_tail = models.BatchInput.get_tail(batch_id, LAST_LINES)

    template = loader.get_template('view.html')

    context = {
        'batch': batch,
        'data_titles': data_titles,
        'data_head': data_head,
        'data_tail' : data_tail,
    }
    return HttpResponse(template.render(context, request))


class PublicAjax(dt.DTView):
    model = models.Batchs
    columns = ['Batch_Id', 'Project_Name','Batch_Version',  'Batch_Received_DateTime', 'Project_Description', 'status', 'input_columns', 'output_columns', 'Solving_Acuracy']
    order_columns = ['Batch_Id', 'Project_Name', 'Batch_Version', 'status']

    def filter_queryset(self, qs):
        from django.db.models import Q

        # public only
        qs = qs.filter(Project_IsPublic=True)

        # search
        sSearch = self.request.GET.get('sSearch', None)

        if sSearch:
            qs = qs.filter(
                Q(Project_Name__istartswith=sSearch) |
                Q(Project_Description__istartswith=sSearch)
            )

        # last at top
        qs = qs.order_by('-Batch_Id')

        return qs


class MyAjax(dt.DTView):
    model = models.Batchs
    columns = ['Batch_Id', 'Project_Name','Batch_Version',  'Batch_Received_DateTime', 'Project_Description', 'status', 'input_columns', 'output_columns', 'Solving_Acuracy']
    order_columns = ['Batch_Id', 'Project_Name', 'Batch_Version', 'status']


    def get(self, request):
        self.request = request
        return super(MyAjax, self).get(request)


    def filter_queryset(self, qs):
        from django.db.models import Q

        # my only
        qs = qs.filter(User_ID__exact=self.request.user)

        # not public
        qs = qs.filter(Project_IsPublic=False)

        # search
        sSearch = self.request.GET.get('sSearch', None)

        if sSearch:
            qs = qs.filter(
                Q(Project_Name__istartswith=sSearch) |
                Q(Project_Description__istartswith=sSearch)
            )

        # last at top
        qs = qs.order_by('-Batch_Id')

        return qs


class Send2Ajax(dt.DTView):
    def get(self, request, batch_id):
        # Query from table BATCH_INPUT_NNN
        # without pk 'index'
        # return JSON
        self.model = models.BatchInput(batch_id)
        self.columns = [ f.name for f in  self.model._meta.get_fields() ][1:] # without 'index' PK
        self.order_columns = self.columns
        return super(Send2Ajax, self).get(request)


# tb
from django import conf

def include_raw(path):
    import os.path

    for template_dir in conf.settings.TEMPLATES[0]['DIRS']:
        filepath = '%s/%s' % (template_dir, path)
        if os.path.isfile(filepath):
            break

    with open(filepath, 'rb') as fp:
        return fp.read()

def tb(request, batch_id):
    return render(request, 'view_tb.html')

