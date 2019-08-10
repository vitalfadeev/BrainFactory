from django import forms
from . import models
from . import helpers
from django.contrib.auth.models import User


class SendForm1(forms.ModelForm):
    class Meta:
        model = models.Batchs
        fields = (
            'Project_Name',
            'Project_FileSourcePathName',
            'Project_Description',
            'Project_IsPublic',
        )
        fields_required = ['Project_Name']
        labels = {
            "Project_Name": "Project name",
            "Project_FileSourcePathName": "File Source",
            "Project_Description": "Description",
            "Project_IsPublic": "Make this project public",
        }


class SendForm2(forms.ModelForm):
    class Meta:
        model = models.Batchs

        fields = (
            'Project_Name',
            #'Project_Description',
            #'Project_IsPublic',

            'Project_ColumnsDescription',
            #'ProjectSource_ColumnsNameForceInput',
            #'ProjectSource_ColumnsNameForceOutput',
            'AnalysisSource_ColumnsNameInput',
            #'AnalysisSource_ColumnsNameOutput',
            'AnalysisSource_ColumnType',
            #'AnalysisSource_Errors',
            #'AnalysisSource_Warnings',
        )
        fields_required = []
        labels = {
            "Project_Name": "Project name",
            "Project_Description": "Description",
            "Project_IsPublic": "Make this project public",
        }
        widgets = {
            'Project_Name'                          : forms.HiddenInput(), #
            #'Project_Description'                   : forms.HiddenInput(),
            #'Project_IsPublic'                      : forms.HiddenInput(),
            'Project_ColumnsDescription'            : forms.HiddenInput(), #
            #'ProjectSource_ColumnsNameForceInput'   : forms.HiddenInput(), # select
            #'ProjectSource_ColumnsNameForceOutput'  : forms.HiddenInput(), # select
            'AnalysisSource_ColumnsNameInput'       : forms.HiddenInput(), #
            #'AnalysisSource_ColumnsNameOutput'      : forms.HiddenInput(), #
            'AnalysisSource_ColumnType'            : forms.HiddenInput(), #
            #'AnalysisSource_Errors'                 : forms.HiddenInput(),
            #'AnalysisSource_Warnings'               : forms.HiddenInput(),
        }


SHAPE_CHOICES = (
    ("DENSE SOFTMAX", "Dense softmax"),
    ("DENSE ELU", "Dense elu"),
    ("DENSE SELU", "Dense selu"),
    ("DENSE SOFTPLUS", "Dense softplus"),
    ("DENSE SOFTSIGN", "Dense softsign"),
    ("DENSE RELU", "Dense relu"),
    ("DENSE TANH", "Dense tanh"),
    ("DENSE SIGMOID", "Dense sigmoid"),
    ("DENSE HARD_SIGMOID", "Dense hard_sigmoid"),
    ("DENSE EXPONENTIAL", "Dense exponential"),
    ("DENSE LINEAR", "Dense linear"),
    ("DROPOUT", "Dropout"),
    ("BATCHNORMALIZATION", "BatchNormalization"),
)

from material import Layout, Row, Column, Fieldset, Span2, Span3, Span5, Span6, Span10
class SendForm3(forms.ModelForm):
    shape_n1 = forms.CharField(label='n')
    shape_c1 = forms.ChoiceField(choices=SHAPE_CHOICES, label='v', widget=forms.Select)

    shape_n2 = forms.CharField(label='n')
    shape_c2 = forms.ChoiceField(choices=SHAPE_CHOICES, label='v', widget=forms.Select)

    shape_n3 = forms.CharField(label='n')
    shape_c3 = forms.ChoiceField(choices=SHAPE_CHOICES, label='v', widget=forms.Select)

    shape_n4 = forms.CharField(label='n')
    shape_c4 = forms.ChoiceField(choices=SHAPE_CHOICES, label='v', widget=forms.Select)

    shape_n5 = forms.CharField(label='n')
    shape_c5 = forms.ChoiceField(choices=SHAPE_CHOICES, label='v', widget=forms.Select)

    class Meta:
        model = models.Batchs
        fields = (
            'ParameterCNN_Loss',
            'ParameterCNN_Optimizer',
            'ParameterCNN_Shape',
        )
        fields_required = []
        labels = {
            "ParameterCNN_Loss": "Loss",
            "ParameterCNN_Optimizer": "Optimizer",
            "ParameterCNN_Shape": "Shape",
        }
        widgets = {
            'ParameterCNN_Shape': forms.HiddenInput(),
        }
    layout = Layout(
        Fieldset("NN Parameters",
            Row('ParameterCNN_Optimizer'),
            Row('ParameterCNN_Loss')
         ),
        Fieldset('Shape',
            Row('shape_n1', 'shape_c1'),
            Row('shape_n2', 'shape_c2'),
            Row('shape_n3', 'shape_c3'),
            Row('shape_n4', 'shape_c4'),
            Row('shape_n5', 'shape_c5'),
        ),
    )