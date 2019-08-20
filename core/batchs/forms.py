import json
from django import forms
from django.utils.safestring import mark_safe
from django.contrib.auth.models import User
from material import Layout, Row, Column, Fieldset, Span2, Span3, Span5, Span6, Span10
from . import models


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


INOUT_CHOICES = [
    ("", ""),
    ("INPUT", "Input"),
    ("OUTPUT", "Output"),
]

class SendForm2(forms.ModelForm):
    class Meta:
        model = models.Batchs

        fields = (
        )
        fields_required = [
        ]
        labels = {
        }
        widgets = {
        }


    def __init__(self, *args, **kwargs):
        super(SendForm2, self).__init__(*args, **kwargs)

        batch = kwargs['instance']
        titles = models.BatchInput(batch.Batch_Id).get_column_names(without_pk=True)
        self.add_desc_fields(titles, batch.Project_ColumnsDescription)
        self.add_inout_fields(titles, batch)

    
    # desc
    def add_desc_fields(self, titles, initials):
        for i, t in enumerate(titles):
            fname = 'desc_{}'.format(i)
            self.fields[fname] = forms.CharField(label='description {}'.format(t),
                 required=False,
                 widget=forms.Textarea(attrs={
                     'cols': '40',
                     'rows': '5'
                 }))
            self.initial[fname] = initials[i] if i < len(initials) else ""


    def get_desc_fields(self):
        for field_name in self.fields:
            if field_name.startswith('desc_'):
                yield self[field_name]


    def get_desc_values(self):
        for name, value in self.cleaned_data.items():
            if name.startswith('desc_'):
                yield (self.fields[name].label, value)


    def save_desc_fields(self, batch):
        batch.Project_ColumnsDescription = []        
        for f, v in self.get_desc_values():
            batch.Project_ColumnsDescription.append(v)
            

    # in / out
    def add_inout_fields(self, titles, batch):
        for i, t in enumerate(titles):
            fname = 'inout_{}'.format(i)
            self.fields[fname] = forms.CharField(label='inout {}'.format(t), required=False, 
                                                 widget=forms.Select(choices=INOUT_CHOICES))

            if t in batch.ProjectSource_ColumnsNameForceInput:
                self.initial[fname] = "INPUT"
            elif t in batch.ProjectSource_ColumnsNameForceOutput:
                self.initial[fname] = "OUTPUT"
            elif t in batch.AnalysisSource_ColumnsNameInput:
                self.initial[fname] = "INPUT"
            elif t in batch.AnalysisSource_ColumnsNameOutput:
                self.initial[fname] = "OUTPUT"


    def get_inout_fields(self):
        for field_name in self.fields:
            if field_name.startswith('inout_'):
                yield self[field_name]


    def get_inout_values(self):
        for name, value in self.cleaned_data.items():
            if name.startswith('inout_'):
                yield (self.fields[name].label, value)


    def save_inout_fields(self, batch):
        batch.ProjectSource_ColumnsNameForceInput = []
        batch.ProjectSource_ColumnsNameForceOutput = []

        titles = models.BatchInput(batch.Batch_Id).get_column_names(without_pk=True) # without 'index' PK
        
        for c, (f, v) in zip(titles, self.get_inout_values()):
            if v == "INPUT":
                if c not in batch.AnalysisSource_ColumnsNameInput:
                    batch.ProjectSource_ColumnsNameForceInput.append(c)
            elif v == "OUTPUT":
                if c not in batch.AnalysisSource_ColumnsNameOutput:
                    batch.ProjectSource_ColumnsNameForceOutput.append(c)
            else:
                pass
            

    def clean(self):
        pass


    def save(self, *args, **kwargs):
        instance = super(SendForm2, self).save(commit=False)
        self.save_desc_fields(instance)
        self.save_inout_fields(instance)
        instance.save()
        return instance
        

class PlainTextWidget(forms.Widget):
    def render(self, name, value, attrs=None, renderer=None):
        return mark_safe(value) if value is not None else ''


class SendForm3(forms.ModelForm):
    class Meta:
        model = models.Batchs
        fields = (
            'ParameterCNN_Loss',
            'ParameterCNN_Optimizer',
            'ParameterCNN_Batch_size',
            'ParameterCNN_Epoch',
        )
        fields_required = []
        labels = {
            "ParameterCNN_Loss": "Loss",
            "ParameterCNN_Optimizer": "Optimizer",
            "ParameterCNN_Batch_size": "Batch size",
            "ParameterCNN_Epoch": "Epoch",
        }
        widgets = {
             'ParameterCNN_Optimizer': forms.Select(choices=models.two_cols(models.PARAMETERCNN_OPTIMIZER), 
                    attrs={
                        'data-tooltips': json.dumps(models.last_col(models.PARAMETERCNN_OPTIMIZER))
                    }),
             'ParameterCNN_Loss': forms.Select(choices=models.two_cols(models.PARAMETERCNN_LOSS), 
                    attrs={
                        'data-tooltips': json.dumps(models.last_col(models.PARAMETERCNN_LOSS))
                    }),
        }

    layout = Layout(
        Fieldset("NN Parameters",
            Row('ParameterCNN_Optimizer'),
            Row('ParameterCNN_Loss'),
            Row('ParameterCNN_Batch_size'),
            Row('ParameterCNN_Epoch')
         ),
        Fieldset('Shape',
            Row('shape_n0', 'shape_c0'),
            Row('shape_n1', 'shape_c1'),
            Row('shape_n2', 'shape_c2'),
            Row('shape_n3', 'shape_c3'),
            Row('shape_n4', 'shape_c4'),
            Row('shape_n5', 'shape_c5'),
            Row('shape_n6', 'shape_c6'),
            Row('shape_n7', 'shape_c7'),
            Row('shape_n8', 'shape_c8'),
            Row('shape_n9', 'shape_c9'),
        ),
    )

    def __init__(self, *args, **kwargs):
        super(SendForm3, self).__init__(*args, **kwargs)
        instance = kwargs['instance']
        self.add_shape_fields(instance.ParameterCNN_Shape)
        
        
    def add_shape_fields(self, initials):
        for i in range(10):
            fname_n = 'shape_n{}'.format(i)
            fname_c = 'shape_c{}'.format(i)

            self.fields[fname_n] = forms.CharField(
                label='' if i in [0,9] else 'Neurons Size',
                max_length=7,
                required=False,
                widget=forms.TextInput(
                    attrs={
                        'data-tooltips': json.dumps(models.last_col(models.SHAPE_CHOICES)),
                    }
                ) if i > 0 and i < 9 else PlainTextWidget()
            )
            self.fields[fname_c] = forms.ChoiceField(
                choices=models.two_cols(models.SHAPE_CHOICES),
                label="Neurons layer type",
                widget=forms.Select(
                    choices=models.two_cols(models.SHAPE_CHOICES),
                    attrs={
                        'data-tooltips': json.dumps(models.last_col(models.SHAPE_CHOICES)),
                    }
                )
            )
            self.initial[fname_n] = initials[i][0] if i < len(initials) else ""
            self.initial[fname_c] = initials[i][1] if i < len(initials) else ""


    def get_shape_values(self):
        for name, value in self.cleaned_data.items():
            if name.startswith('shape_n'):
                value_n = value
                value_c = self.cleaned_data[name.replace('shape_n', 'shape_c')]
                yield (self.fields[name].label, value_n, value_c)


    def save(self, *args, **kwargs):
        instance = super(SendForm3, self).save(commit=False)
        instance.ParameterCNN_Shape = []
        for name, vn, vc in self.get_shape_values():
            instance.ParameterCNN_Shape.append((vn, vc)) 
        instance.save()
        return instance


class GraphForm(forms.ModelForm):
    class Meta:
        model = models.Graphs

        fields = (
            'GraphType',
            'X',
            'Y',
            'Z',
            'color',
            #'Animation_Frame',
            'ColorScales',
        )
        fields_required = []
        labels = {
            'GraphType'         :'Graph Type',
            'X'                 :'X',
            'Y'                 :'Y',
            'Z'                 :'Z',
            'color'             :'color',
            #'Animation_Frame'   :'Animation Frame',
            'ColorScales'       :'Color Scales',
        }

    def __init__(self, batch, *args, **kwargs):
        super(GraphForm, self).__init__(*args, **kwargs)

        columns = [(col, col) for col in batch.titles]
        color_columns = [(col, col) for (col, typ) in zip(batch.titles, batch.types) if typ in ['OPTION', 'BINARY'] ]

        self.fields['X'] = forms.ChoiceField(choices = columns)
        self.fields['Y'] = forms.ChoiceField(choices = columns)
        self.fields['Z'] = forms.ChoiceField(choices = columns)

        if color_columns:
            self.fields['color'] = forms.ChoiceField(choices = color_columns)
        else:
            self.fields['color'] = forms.CharField(max_length=255)

        if 'instance' not in kwargs:
            if len(columns) >= 1:
                self.initial['X'] = columns[0][0]
            if len(columns) >= 2:
                self.initial['Y'] = columns[1][0]
            if len(columns) >= 3:
                self.initial['Z'] = columns[2][0]
            if len(color_columns) >= 1:
                self.initial['color'] = color_columns[0][0]
            self.initial['GraphType'] = "1"
            self.initial['ColorScales'] = "1"


    #def is_valid(self, *args, **kwargs):
    #    super(GraphForm, self).is_valid(*args, **kwargs)
    #    #return True
