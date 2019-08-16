from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET
from django.http import HttpResponse
from django.template import loader
from django.conf import settings
from django.views.generic import TemplateView
from django import conf
from django.shortcuts import redirect
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
    from django.http import HttpResponseRedirect, Http404
    from . import models


    # check access
    batch = models.Batchs.objects.get(Batch_Id=batch_id)

    if batch.Project_IsPublic:
        pass
    else:
        if batch.User_ID == request.user:
            pass
        else:
            raise Http404

    # render
    # input
    titles = batch.titles

    errors        = batch.errors
    error_dataset = batch.AnalysisSource_Errors.get("DATASET", "")
    warnings      = batch.warnings
    types         = batch.types

    # solved
    model_solved = models.BatchSolved(batch.Batch_Id)

    is_data_solved = model_solved.has_table()

    if is_data_solved:
        titles_solved = model_solved.get_column_names(without_pk=True)
        types_solved  = model_solved.get_column_types(without_pk=True)
    else:
        titles_solved = []
        types_solved  = []

    template = loader.get_template('view.html')

    context = {
        'batch': batch,
        'titles': titles,
        'has_errors': any(errors),
        'errors': errors,
        'error_dataset': error_dataset,
        'has_warnings': any(warnings),
        'warnings': warnings,
        'types': types,
        'is_data_solved': is_data_solved,
        'titles_solved': titles_solved,
        'types_solved': types_solved,
    }

    return HttpResponse(template.render(context, request))


@login_required
def view_tb(request, batch_id):
    return render(request, 'view_tb.html')


@login_required
def view_tb_self(request, batch_id):
    return render(request, 'view_tb_self.html')


def serve_file(filename):
    response = HttpResponse(mimetype="text/html")
    for line in open(filename):
        response.write(line)
    return response

def serve_file2(filename):
    image_data = open(filename, "rb").read()
    return HttpResponse(image_data, content_type="text/html")

def view_tb_static(request, batch_id=None):
    return serve_file2(settings.BASE_DIR + '/static/tensorboard/index.html')


# public
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


#@login_required
class my_ajax(dt.DTView):
    model = models.Batchs
    columns = ['Batch_Id', 'Project_Name','Batch_Version',  'Batch_Received_DateTime', 'Project_Description', 'status', 'input_columns', 'output_columns', 'Solving_Acuracy']
    order_columns = ['Batch_Id', 'Project_Name', 'Batch_Version', 'status']


    def get(self, request):
        self.request = request
        return super(my_ajax, self).get(request)


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


#@login_required
class send2_id_ajax(dt.DTView):
    def get(self, request, batch_id):
        # Query from table BATCH_INPUT_NNN
        # without pk 'index'
        # return JSON
        self.model = models.BatchInput(batch_id)
        self.columns = self.model.get_field_names(without_pk=True)
        self.order_columns = self.columns
        return super(send2_id_ajax, self).get(request)


#@login_required
class view_id_solved_ajax(dt.DTView):
    def get(self, request, batch_id):
        # Query from table BATCH_INPUT_NNN
        # without pk 'index'
        # return JSON
        model_solved = models.BatchSolved(batch_id)
        self.model =  model_solved
        self.columns = model_solved.get_field_names(without_pk=True)
        self.order_columns = self.columns
        res = super(view_id_solved_ajax, self).get(request)
        return super(view_id_solved_ajax, self).get(request)


@login_required
def view_export_input_csv(request, batch_id):
    from djqscsv import render_to_csv_response

    model = models.BatchInput(batch_id)
    qs = model.objects.all()
    header = model.get_header_map()
    return render_to_csv_response(qs, field_header_map=header)


@login_required
def view_export_solved_csv(request, batch_id):
    from djqscsv import render_to_csv_response

    model = models.BatchSolved(batch_id)
    qs = model.objects.all()
    header = model.get_header_map()
    return render_to_csv_response(qs, field_header_map=header)


@login_required
def view_export_input_xls(request, batch_id):
    from excel_response import ExcelResponse
    model = models.BatchInput(batch_id)
    qs = model.objects.all()
    return ExcelResponse(qs)


@login_required
def view_export_solved_xls(request, batch_id):
    from excel_response import ExcelResponse
    model = models.BatchSolved(batch_id)
    qs = model.objects.all()
    return ExcelResponse(qs)



def redirect_view(request, prefix=None, tail=None, batch_id=None):
    from django.http import HttpResponseRedirect, Http404
    if tail:
        #response = redirect('/static/' + tail)
        return HttpResponseRedirect('/static/' + prefix + '/' + tail)
    else:
        raise Http404
