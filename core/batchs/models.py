import sys
import collections
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
import jsonfield
from .helpers import uploads_directory_path
from .validators import validate_file_extension
from . import dymo


BATCH_ACTION_CHOICES = [
    ("TRAIN", "Train"),
    ("SOLVE", "Solve"),
    ("EVALUATE",  "Evaluate")
]

PROJECT_SOURCEMODE_CHOICES = [
    ("DB", "DB"),
    ("FILE", "File"),
]

BATCH_STATE_DONE = 'Done'
BATCH_STATE_WAIT = 'Wait'

PARAMETERCNN_LOSS = [
    ("BINARYCROSSENTROPY"   , "BinaryCrossentropy", """
        <i>Use this cross-entropy loss<br> 
        when there are only two label classes<br>
        assumed to be 0 and 1).<br> 
        For each example, there should be a single<br>
        floating-point value per prediction.</i>"
        """),
    ("SQUAREDHINGE"         , "SquaredHinge",       "<i>Computes the squared hinge loss<br>y_true values are expected to be -1 or 1. If binary (0 or 1) labels are provided we will convert them to -1 or 1.</i>"),
    ("POISSON"              , "Poisson",            "<i>Computes the Poisson loss<br>loss = y_pred - y_true * log(y_pred)</i>"),
    ("MEANSQUAREDERROR"     , "MeanSquaredError",   "<i>Computes the mean of squares of errors between labels and predictions</i>"),
    ("MEANABSOLUTEERROR"    , "MeanAbsoluteError",  "<i>Computes the mean of absolute difference between labels and predictions</i>"),
    ("HUBER"                , "Huber",              "<i>Computes the Huber loss<br>0.5 * x^2                  if |x| <= d<br>0.5 * d^2 + d * (|x| - d)  if |x| > d</i>"),
    ("HINGE"                , "Hinge",              "<i>Computes the hinge loss <br>y_true values are expected to be -1 or 1. If binary (0 or 1) labels are provided we will convert them to -1 or 1.</i>"),
    ("COSINESIMILARITY"     , "CosineSimilarity",   "<i>Computes the cosine similarity</i>"),
]

PARAMETERCNN_OPTIMIZER = [
    ("SGD"      , "SGD",        "<i>Stochastic gradient descent optimizer</i>"),
    ("RMSPROP"  , "RMSprop",    "<i>RMSProp optimizer</i>"),
    ("ADADELTA" , "Adadelta",   """
        <i>Adadelta optimizer.<br>
        Adadelta is a more robust extension<br>
        of Adagrad that adapts learning rates <br>
        based on a moving window of gradient updates,<br> 
        instead of accumulating all past gradients. <br>
        This way, Adadelta continues learning even <br>
        when many updates have been done.</i>
        """
    ),
    ("ADAM"     , "Adam",       "<i>Adam optimizer</i>"),
    ("ADAMAX"   , "Adamax",     "<i>Adamax optimizer", "It is a variant of Adam based on the infinity norm. Default parameters follow those provided in the paper.</i>"),
    ("NADAM"    , "Nadam",      "<i>Nesterov Adam optimizer.<br>Much like Adam is essentially RMSprop with momentum, Nadam is Adam RMSprop with Nesterov momentum.</i>")
]

SHAPE_CHOICES = (
    ("DENSE SOFTMAX"        , "Dense softmax"       , "softmax"),
    ("DENSE ELU"            , "Dense elu"           , "exponential linear activation: x if x > 0 and alpha * (exp(x)-1) if x < 0."),
    ("DENSE SELU"           , "Dense selu"          , "scaled exponential unit activation: scale * elu(x, alpha)."),
    ("DENSE SOFTPLUS"       , "Dense softplus"      , "softplus activation: log(exp(x) + 1)."),
    ("DENSE SOFTSIGN"       , "Dense softsign"      , "softsign activation: x / (abs(x) + 1)"),
    ("DENSE RELU"           , "Dense relu"          , "Rectified Linear Unit"),
    ("DENSE TANH"           , "Dense tanh"          , "With default values, it returns element-wise max(x, 0)."),
    ("DENSE SIGMOID"        , "Dense sigmoid"       , """
        Otherwise, it follows: <br>
        f(x) = max_value for x >= max_value, <br>
        f(x) = x for threshold <= x < max_value, <br>
        f(x) = alpha * (x - threshold) otherwise.
        """),
    ("DENSE HARD_SIGMOID"   , "Dense hard_sigmoid"  , """
        Hyperbolic tangent activation function<br>"
        keras.activations.sigmoid(x)<br>
        0 if x < -2.5<br>
        1 if x > 2.5<br>
        0.2 * x + 0.5 if -2.5 <= x <= 2.5."""),
    ("DENSE EXPONENTIAL"    , "Dense exponential"   , "Exponential (base e) activation function"),
    ("DENSE LINEAR"         , "Dense linear"        , "Linear (i.e. identity) activation function"),
    ("DROPOUT"              , "Dropout"             , """
        Dropout works by probabilistically removing,<br>
        or “dropping out,” inputs to a layer, <br>
        which may be input variables in the data sample <br>
        or activations from a previous layer. <br>
        It has the effect of simulating a large number<br>
        of networks with very different network structure <br>
        and, in turn, making nodes in the network generally <br>
        more robust to the inputs."""),
    ("BATCHNORMALIZATION"   , "BatchNormalization"  , """
        The layer will transform inputs so that they are standardized, 
        meaning that they will have a mean of zero and a standard deviation of one."""),
)

def two_cols(data):
    return [row[:2] for row in data]

def last_col(data):
    return [row[-1] for row in data]


class Batchs(models.Model):
    Batch_Id                                = models.AutoField(primary_key=True)
    Batch_Received_DateTime                 = models.DateTimeField(auto_now=True)
    Batch_Version                           = models.IntegerField(default=0)
    Batch_Action                            = models.CharField(max_length=255, default="TRAIN", choices=BATCH_ACTION_CHOICES)

    User_ID                                 = models.ForeignKey(User, on_delete=models.CASCADE)
    Project_Name                            = models.CharField(max_length=255)
    Project_Description                     = models.TextField(default="", blank=True)
    Project_IsPublic                        = models.BooleanField(default=False)
    Project_FileSourcePathName              = models.FileField(upload_to=uploads_directory_path,
                                                               validators=[validate_file_extension])
    Project_ColumnsDescription              = jsonfield.JSONField(load_kwargs={'object_pairs_hook': collections.OrderedDict}, default=[]) # [,]
    ProjectSource_ColumnsNameForceInput     = jsonfield.JSONField(load_kwargs={'object_pairs_hook': collections.OrderedDict}, default=[]) # [,]
    ProjectSource_ColumnsNameForceOutput    = jsonfield.JSONField(load_kwargs={'object_pairs_hook': collections.OrderedDict}, default=[]) # [,]
    
    AnalysisSource_ColumnsNameInput         = jsonfield.JSONField(load_kwargs={'object_pairs_hook': collections.OrderedDict}, default=[]) # [,]
    AnalysisSource_ColumnsNameOutput        = jsonfield.JSONField(load_kwargs={'object_pairs_hook': collections.OrderedDict}, default=[]) # [,]
    AnalysisSource_ColumnType               = jsonfield.JSONField(load_kwargs={'object_pairs_hook': collections.OrderedDict}, default=[]) # [,]
    AnalysisSource_Errors                   = jsonfield.JSONField(load_kwargs={'object_pairs_hook': collections.OrderedDict}, default={}) # [,]
    AnalysisSource_Warnings                 = jsonfield.JSONField(load_kwargs={'object_pairs_hook': collections.OrderedDict}, default={}) # [,]

    ParameterCNN_SettingAuto                = models.BooleanField(default=True)
    ParameterCNN_Loss                       = models.CharField(max_length=255, default=PARAMETERCNN_LOSS[0][0], choices=two_cols(PARAMETERCNN_LOSS), help_text="")
    ParameterCNN_Optimizer                  = models.CharField(max_length=255, default=PARAMETERCNN_OPTIMIZER[0][0], choices=two_cols(PARAMETERCNN_OPTIMIZER) )
    ParameterCNN_Shape                      = jsonfield.JSONField(load_kwargs={'object_pairs_hook': collections.OrderedDict}, default=[]) # []
    ParameterCNN_Batch_size                 = models.IntegerField(default=0)
    ParameterCNN_Epoch                      = models.IntegerField(default=0)

    Solving_DateTimeSending                 = models.DateTimeField(auto_now=False, blank=True, null=True)
    Solving_DelayElapsed                    = models.IntegerField(default=0)
    Solving_Acuracy                         = models.BooleanField(default=False)
    Solving_Loss                            = models.TextField(blank=True, null=True)
    Solving_FilePathBrainModel              = models.FileField(upload_to=uploads_directory_path, blank=True, null=True)
    Solving_TextError                       = models.TextField(blank=True, null=True)
    Solving_TextWarning                     = models.TextField(blank=True, null=True)

    @property
    def input_columns(self):
        # force in + (analyser in - force out)
        columns = []

        for c in self.ProjectSource_ColumnsNameForceInput:
            columns.append(c)

        for c in self.AnalysisSource_ColumnsNameInput:
            if c not in self.ProjectSource_ColumnsNameForceOutput:
                columns.append(c)

        return columns


    @property
    def output_columns(self):
        # force out + (analyser out - force in)
        columns = []

        for c in self.ProjectSource_ColumnsNameForceOutput:
            columns.append(c)

        for c in self.AnalysisSource_ColumnsNameOutput:
            if c not in self.ProjectSource_ColumnsNameForceInput:
                columns.append(c)

        return columns


    def has_nn_data(self):
        if self.input_columns and self.output_columns:
            return True
        else:
            return False


    @property
    def status(self):
        if self.has_nn_data():
            return BATCH_STATE_DONE
        else:
            return BATCH_STATE_WAIT

    @property
    def types(self):
        titles = self.titles
        return [self.AnalysisSource_ColumnType.get(t, "") for t in titles]

    @property
    def warnings(self):
        titles = self.titles
        return [self.AnalysisSource_Warnings.get(t, "") for t in titles]

    @property
    def errors(self):
        titles = self.titles
        return [self.AnalysisSource_Errors.get(t, "") for t in titles]

    @property
    def titles(self):
        titles = BatchInput(self.Batch_Id).get_column_names(without_pk=True)
        return titles


# 10 possible Graph Type
GRAPH_CHOICES = (
    ('1',
        '1 (points)',
        'note : colors only can have columns of type OPTION or BINARY'
    ),
    ('2',
        '2 (points)',
        'note : colors only can have columns of type OPTION or BINARY'
    ),
    ('3',
        '3 (points)',
        'note : colors only can have columns of type OPTION or BINARY'
    ),
    ('4',
        '4 (grid)',
        'note : colors only can have columns of type OPTION or BINARY'
    ),
    ('5',
        '5 (lines)',
        ''
    ),
    ('6',
        '6',
        'note : colors only can have columns of type OPTION or BINARY'
    ),
    ('7',
        '7 (area)',
        ''
    ),
    ('8',
        '8 (points colored)',
        ''
    ),
    ('9',
        '9',
        'note : colors only can have columns of type OPTION or BINARY'
    ),
    ('10',
        '10 (3D)',
        'note : colors only can have columns of type OPTION or BINARY'
    ),
)

def BatchInput(batch_id):
    """
    Dynamic model factory
    example:
        model = models.BatchInput(batch_id)
    """
    cls     = "BatchInput{}".format(batch_id)
    table   = "BATCH_INPUT_{}".format(batch_id)
    app     = 'core'
    module  = 'batchs'
    pk      = 'index'

    cls = dymo.get_dynamic_model(
        (models.Model, dymo.DymoMixin),cls, table, app, module, pk
    )

    return cls


def BatchSolved(batch_id):
    """
    Dynamic model factory
    example:
        model = models.BatchInput(batch_id)
    """
    cls     = "BatchSolved{}".format(batch_id)
    table   = "BATCH_SOLVED_{}".format(batch_id)
    app     = 'core'
    module  = 'batchs'
    pk      = 'index'

    cls = dymo.get_dynamic_model(
        (models.Model, dymo.DymoMixin),cls, table, app, module, pk
    )

    return cls


COLORSET_CHOICES = (
    ('1', 'light24'),
    ('2', 'pastel1'),
    ('3', 'bold'),
    ('4', 'inferno'),
    ('5', 'GnBu'),
    ('6', 'OrRd'),
    ('7', 'amp'),
    ('8', 'ice'),
    ('9', 'rdbu'),
    ('10', 'pubu'),
    ('11', 'red'),
)


class Graphs(models.Model):
    Batch_Id        = models.OneToOneField(Batchs, on_delete=models.CASCADE, primary_key=True)
    GraphType       = models.CharField(max_length=255, default=GRAPH_CHOICES[0][0], choices=two_cols(GRAPH_CHOICES))
    X               = models.CharField(max_length=255, default='')
    Y               = models.CharField(max_length=255, default='')
    Z               = models.CharField(max_length=255, default='')
    color           = models.CharField(max_length=255, default='#ccc')
    #Animation_Frame = models.CharField(max_length=255, default="")
    ColorScales     = models.CharField(max_length=255, default='1', choices=COLORSET_CHOICES)
