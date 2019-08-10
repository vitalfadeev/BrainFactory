from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template import loader
from django.conf import settings
from material import Layout, Row, Fieldset
from . import models


# signup: allauth.account.forms.SignupForm
# signup: allauth.socialaccount.forms.SignupForm
# add_email: allauth.account.forms.AddEmailForm
# change_password: allauth.account.forms.ChangePasswordForm
# reset_password: allauth.account.forms.ResetPasswordForm

# Create your views here.
def home(request):
    return render(request, 'home.html')


@login_required
def my(request):
    from . import models

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
    from . import helpers

    # check access
    batch = models.Batchs.objects.get(Batch_Id=batch_id)

    if batch.User_ID == request.user:
        pass
    else:
        raise Http404

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        form = forms.SendForm2(request.POST, request.FILES, instance=batch)

        if form.is_valid():
            batch = form.save(commit=False)
            batch.save()
            return HttpResponseRedirect('/send2/{}'.format(batch.Batch_Id))

        else:
            return HttpResponseRedirect('/send2/{}'.format(batch.Batch_Id))

    # if a GET (or any other method) we'll create a blank form
    else:
        def as_dict(d):
            return d if isinstance(d, dict) else {}

        def as_list(d):
            return d if isinstance(d, list) else []

        form    = forms.SendForm2(instance=batch)
        colsin  = batch.AnalysisSource_ColumnsNameInput
        colsout = batch.AnalysisSource_ColumnsNameOutput
        cols    = list(colsin) + list(colsout)

        errs    = [as_dict(batch.AnalysisSource_Errors).get(c, "")   for c in cols]
        warn    = [as_dict(batch.AnalysisSource_Warnings).get(c, "") for c in cols]
        types   = [as_dict(batch.AnalysisSource_ColumnType).get(c, "") for c in cols]
        has_errs = any(errs)
        has_warn = any(warn)
        dataset_err = as_dict(batch.AnalysisSource_Errors).get("DATASET", "")

        ttls    = models.BatchInput.get_titles(batch.Batch_Id)
        data    = models.BatchInput.get_head(batch.Batch_Id, 5)

        # reorder fields
        head    = []
        for row in data:
            r = []
            for c in cols:
                try: i = ttls.index(c)
                except ValueError: i = ttls.index('"' + c + '"')
                r.append(row[i])
            head.append(r)

        template = loader.get_template('send2.html')

        context = {
            'form': form,
            'batch': batch,
            'cols': cols,
            'head': head,
            'errs': errs,
            'warn': warn,
            'types': types,
            'dataset_err': dataset_err,
            'has_errs': has_errs,
            'has_warn': has_warn,
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

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        form = forms.SendForm3(request.POST, request.FILES, instance=batch)

        if form.is_valid():
            batch = form.save(commit=False)
            batch.save()
            return HttpResponseRedirect('/send3/{}'.format(batch.Batch_Id))

        else:
            return HttpResponseRedirect('/send3/{}'.format(batch.Batch_Id))

    # if a GET (or any other method) we'll create a blank form
    else:
        form    = forms.SendForm3(instance=batch)
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
    data_titles = models.BatchInput.get_titles(batch_id)
    data_head = models.BatchInput.get_head(batch_id, FIRST_LINES)
    data_tail = models.BatchInput.get_tail(batch_id, LAST_LINES)
    """
    #
    if batch.AnalysisSource_ColumnsNameInput:
        analyser_cols_input = json.loads(batch.AnalysisSource_ColumnsNameInput)
    else:
        analyser_cols_input = []

    #
    if batch.AnalysisSource_ColumnsNameOutput:
        analyser_cols_output = json.loads(batch.AnalysisSource_ColumnsNameOutput)
    else:
        analyser_cols_output = []

    #
    if batch.AnalysisSource_ColumnType:
        analyser_cols_type_in = []
        types = json.loads(batch.AnalysisSource_ColumnType)
        for cname in analyser_cols_input:
            tp = types.get(cname, None)
            analyser_cols_type_in.append( tp )
    else:
        analyser_cols_type_in = []

    #
    if batch.AnalysisSource_ColumnType:
        analyser_cols_type_out = []
        types = json.loads(batch.AnalysisSource_ColumnType)
        for cname in analyser_cols_output:
            tp = types[cname]
            analyser_cols_type_out.append( tp )
    else:
        analyser_cols_type_out = []

    #
    analyser_first_5 = []
    analyser_last_5 = []
    """

    template = loader.get_template('view.html')

    context = {
        'batch': batch,
        'data_titles': data_titles,
        'data_head': data_head,
        'data_tail' : data_tail,
        #'analyser_errors'       : helpers.from_json(batch.AnalysisSource_Errors, {}),
        #'analyser_warnings'     : helpers.from_json(batch.AnalysisSource_Warnings, {}),
        #'analyser_cols_input'   : analyser_cols_input,
        #'analyser_cols_output'  : analyser_cols_output,
        #'analyser_cols_type_in' : analyser_cols_type_in,
        #'analyser_cols_type_out': analyser_cols_type_out,
        #'analyser_first_5'      : analyser_first_5,
        #'analyser_last_5'       : analyser_last_5,
    }
    return HttpResponse(template.render(context, request))
