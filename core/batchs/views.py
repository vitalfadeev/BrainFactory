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
            form.save()

            if 'btn_next' in request.POST:
                return HttpResponseRedirect('/send3/{}'.format(batch.Batch_Id))
        else:
            print(form.errors)

    # GET
    else:
        form = forms.SendForm2(instance=batch)

    # render
    titles = models.BatchInput.get_titles(batch.Batch_Id)

    desc_fields   = form.get_desc_fields
    inout_fields  = form.get_inout_fields
    errors        = [batch.AnalysisSource_Errors.get(t, "") for t in titles]
    error_dataset = batch.AnalysisSource_Errors.get("DATASET", "")
    warnings      = [batch.AnalysisSource_Warnings.get(t, "") for t in titles]
    types         = [batch.AnalysisSource_ColumnType.get(t, "") for t in titles]
    head          = models.BatchInput.get_head(batch.Batch_Id, 5)

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
        'head': head,
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
            form.save()
            return HttpResponseRedirect('/send3/{}'.format(batch.Batch_Id))

        else:
            print(form.errors)
            return HttpResponseRedirect('/send3/{}'.format(batch.Batch_Id))

    # if a GET (or any other method) we'll create a blank form
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
