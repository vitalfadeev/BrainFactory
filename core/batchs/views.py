from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic import DetailView
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect
from django.views.decorators.http import require_GET
from django.http import HttpResponseForbidden
from django.urls import resolve
from django.urls import reverse
from django.views.generic import FormView
from django.views.generic.detail import SingleObjectMixin
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.template import loader
from django.conf import settings
from django.views.generic import TemplateView
from django.views import View
from django import conf
from django.shortcuts import redirect
from . import models
from . import forms
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

    # POST
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

    # GET
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
            return HttpResponseRedirect('/view/{}'.format(batch.Batch_Id))

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


@login_required
def view(request, batch_id):
    return HttpResponseRedirect('/view/{}/project'.format(batch_id))


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


@method_decorator(login_required, name='dispatch')
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


@method_decorator(login_required, name='dispatch')
class send2_id_ajax(dt.DTView):
    def get(self, request, batch_id):
        # Query from table BATCH_INPUT_NNN
        # without pk 'index'
        # return JSON
        self.model = models.BatchInput(batch_id)
        self.columns = self.model.get_field_names(without_pk=True)
        self.order_columns = self.columns
        return super(send2_id_ajax, self).get(request)


@method_decorator(login_required, name='dispatch')
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
        return HttpResponseRedirect('/static/' + prefix + '/' + tail)
    else:
        raise Http404


@method_decorator(login_required, name='dispatch')
class ProjectView(DetailView):
    def get(self, request, batch_id, *args, **kwargs):
        batch = models.Batchs.objects.get(Batch_Id=batch_id, User_ID=request.user)

        context = {
            "batch": batch,
            "batch_id": batch_id,
            'url_name': resolve(request.path_info).url_name,
        }
        return render(request, 'view_project_data.html', context)


@method_decorator(login_required, name='dispatch')
class DataInputView(DetailView):
    def get(self, request, batch_id, *args, **kwargs):
        from django.http import HttpResponseRedirect, Http404
        from . import models

        # check access
        batch = models.Batchs.objects.get(Batch_Id=batch_id, User_ID=request.user)

        # input
        titles = batch.titles

        errors = batch.errors
        error_dataset = batch.AnalysisSource_Errors.get("DATASET", "")
        warnings = batch.warnings
        types = batch.types

        # solved
        model_solved = models.BatchSolved(batch.Batch_Id)

        is_data_solved = model_solved.has_table()

        if is_data_solved:
            titles_solved = model_solved.get_column_names(without_pk=True)
            types_solved = model_solved.get_column_types(without_pk=True)
        else:
            titles_solved = []
            types_solved = []

        template = loader.get_template('view.html')

        context = {
            "batch_id": batch_id,
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
            'url_name': resolve(request.path_info).url_name,
        }
        return render(request, 'view_data_input.html', context)


@method_decorator(login_required, name='dispatch')
class DataSolvingView(DetailView):
    def get(self, request, batch_id, *args, **kwargs):
        batch = models.Batchs.objects.get(Batch_Id=batch_id, User_ID=request.user)

        context = {
            "batch": batch,
            "batch_id": batch_id,
            'url_name': resolve(request.path_info).url_name,
        }
        return render(request, 'view_data_solved.html', context)


@method_decorator(login_required, name='dispatch')
class SolvingView(DetailView):
    def get(self, request, batch_id, *args, **kwargs):
        from django.http import HttpResponseRedirect, Http404
        from . import models

        # check access
        batch = models.Batchs.objects.get(Batch_Id=batch_id, User_ID=request.user)

        # render
        # input
        titles = batch.titles

        errors = batch.errors
        error_dataset = batch.AnalysisSource_Errors.get("DATASET", "")
        warnings = batch.warnings
        types = batch.types

        # solved
        model_solved = models.BatchSolved(batch.Batch_Id)

        is_data_solved = model_solved.has_table()

        if is_data_solved:
            titles_solved = model_solved.get_column_names(without_pk=True)
            types_solved = model_solved.get_column_types(without_pk=True)
        else:
            titles_solved = []
            types_solved = []

        template = loader.get_template('view.html')

        context = {
            'batch': batch,
            'batch_id': batch_id,
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
            'url_name': resolve(request.path_info).url_name,
        }
        return render(request, 'view_solving_informations.html', context)


@method_decorator(login_required, name='dispatch')
class GraphView(FormView):
    model = models.Graphs
    pk_url_kwarg = 'batch_id'
    form_class = forms.GraphForm
    template_name = 'view_graph.html'

    def get(self, request, batch_id, *args, **kwargs):
        from . import graphs

        self.batch_id = batch_id
        batch = models.Batchs.objects.get(Batch_Id=batch_id, User_ID=request.user)

        try:
            instance = models.Graphs.objects.get(Batch_Id=batch_id)
            form = self.form_class(batch, instance=instance)
            GraphType = instance.GraphType
            x = instance.X
            y = instance.Y
            z = instance.Z
            color = instance.color
            colorset = instance.ColorScales

        except models.Graphs.DoesNotExist:
            form = self.form_class(batch, initial=self.initial)
            GraphType = form.initial['GraphType']
            x = form.initial['X']
            y = form.initial['Y']
            z = form.initial['Z']
            color = None
            colorset = form.initial['ColorScales']

        try:
            if GraphType == "1":
                graph_div = graphs.g1(batch_id, x, y, color, colorset)
            elif GraphType == "2":
                graph_div = graphs.g2(batch_id, x, y, color, colorset)
            elif GraphType == "3":
                graph_div = graphs.g3(batch_id, x, y, color, colorset)
            elif GraphType == "4":
                graph_div = graphs.g4(batch_id, x, y, z, color, colorset)
            elif GraphType == "5":
                graph_div = graphs.g5(batch_id, color, colorset)
            elif GraphType == "6":
                graph_div = graphs.g6(batch_id, x, y, color, z, colorset)
            elif GraphType == "7":
                graph_div = graphs.g7(batch_id, x, y, colorset)
            elif GraphType == "8":
                graph_div = graphs.g8(batch_id, x, y, colorset)
            elif GraphType == "9":
                graph_div = graphs.g9(batch_id, x, y, color, colorset)
            elif GraphType == "10":
                graph_div = graphs.g10(batch_id, x, y, z, color, colorset)
            else:
                graph_div = ''

        except Exception as e:
            graph_div = """<div class="card-panel yellow lighten-5">
                            {}
                           </div>
                        """.format(repr(e))

        context = {
            'form': form,
            'batch_id': batch_id,
            'graph_div': graph_div,
            'url_name': resolve(request.path_info).url_name,
        }
        return render(request, self.template_name, context)

    def post(self, request, batch_id, *args, **kwargs):
        self.batch_id = batch_id
        batch = models.Batchs.objects.get(Batch_Id=batch_id, User_ID=request.user)

        try:
            instance = models.Graphs.objects.get(Batch_Id=batch_id)
            form = self.form_class(batch, request.POST)

        except models.Graphs.DoesNotExist:
            form = self.form_class(batch, request.POST)


        if form.is_valid():
            instance = form.save(commit=False)
            instance.Batch_Id = batch
            instance.save()
            url = self.get_success_url()
            return HttpResponseRedirect(url)
        else:
            return self.form_invalid(form)

    def get_form(self, form_class=None):
        return self.form_class(self.batch_id, **self.get_form_kwargs())

    def get_success_url(self):
        return reverse('view_id_graph', kwargs={'batch_id': self.batch_id})


@method_decorator(login_required, name='dispatch')
class TensorboardView(DetailView):
    def get(self, request, batch_id, *args, **kwargs):
        context = {
            "batch_id": batch_id,
            'url_name': resolve(request.path_info).url_name,
        }
        return render(request, 'view_tensorboard.html', context)


def serve_file(filename):
    image_data = open(filename, "rb").read()
    return HttpResponse(image_data, content_type="text/html")


def view_tensorboard_engine(request, batch_id=None):
    return serve_file(settings.BASE_DIR + '/static/tensorboard/index.html')


