import collections
from django.db import models
from django.contrib.auth.models import User
import jsonfield
from .helpers import uploads_directory_path
from .validators import validate_file_extension


BATCH_ACTION_CHOICES = [
    ("TRAIN", "Train"),
    ("SOLVE", "Solve"),
    ("EVALUATE",  "Evaluate")
]

PROJECT_SOURCEMODE_CHOICES = [
    ("DB", "DB"),
    ("FILE", "File"),
]

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

    Solving_DateTimeSending                 = models.DateTimeField(auto_now=False, blank=True, null=True)
    Solving_DelayElapsed                    = models.IntegerField(default=0)
    Solving_Acuracy                         = models.BooleanField(default=False)
    Solving_Loss                            = models.TextField(blank=True, null=True)
    Solving_FilePathBrainModel              = models.FileField(upload_to=uploads_directory_path, blank=True, null=True)
    Solving_TextError                       = models.TextField(blank=True, null=True)
    Solving_TextWarning                     = models.TextField(blank=True, null=True)


class BatchInput:
    @classmethod
    def get_titles(cls, batch_id):
        from sqlalchemy.sql import text
        from . import helpers

        table = helpers.get_batch_input_table_name(batch_id)

        with helpers.get_db_connection() as con:
            sql = text("""
                SELECT * FROM {} LIMIT 1 
                """.format(table))
            result = con.execute(sql)

            titles = result.keys()

            titles.pop(0) # remove PK

            return titles


    @classmethod
    def get_head(cls, batch_id, limit=5, without_pk=True):
        from sqlalchemy.sql import text
        from . import helpers

        table = helpers.get_batch_input_table_name(batch_id)

        with helpers.get_db_connection() as con:
            sql = text("""
                SELECT * FROM {} LIMIT :limit 
                """.format(table))
            result = con.execute(sql, limit=limit)

            if without_pk:
                rows = [row[1:] for row in result] # without PK
            else:
                rows = [row for row in result]

            return rows


    @classmethod
    def get_tail(cls, batch_id, limit=5):
        from sqlalchemy.sql import text
        from . import helpers

        table = helpers.get_batch_input_table_name(batch_id)

        with helpers.get_db_connection() as con:
            # rows count
            sql = text("""
                SELECT count(*) as cnt FROM {} 
                """.format(table))
            result = con.execute(sql)

            # offset
            cnt = result.first()['cnt']
            offset = cnt - limit

            # tail
            sql = text("""
                SELECT * FROM {} LIMIT :limit OFFSET :offset  
                """.format(table))
            result = con.execute(sql, offset=offset, limit=limit)

            rows = [row for row in result]

            return rows


def create_model(name, fields=None, app_label='', module='', options=None, admin_opts=None):
    """
    Create specified model
    """
    class Meta:
        # Using type('Meta', ...) gives a dictproxy error during model creation
        pass

    if app_label:
        # app_label must be set using the Meta inner class
        setattr(Meta, 'app_label', app_label)

    # Update Meta with any options that were provided
    if options is not None:
        for key, value in options.  items():
            setattr(Meta, key, value)

    # Set up a dictionary to simulate declarations within a class
    attrs = {'__module__': module, 'Meta': Meta}

    # Add in any fields that were provided
    if fields:
        attrs.update(fields)

    # Create the class, which automatically triggers ModelBase processing
    model = type(name, (models.Model,), attrs)

    # Create an Admin class if admin options were provided
    if admin_opts is not None:
        class Admin(admin.ModelAdmin):
            pass
        for key, value in admin_opts:
            setattr(Admin, key, value)
        admin.site.register(model, Admin)

    return model


def create_batch_input_model(batch_id):
    from_table = "BATCH_INPUT_{}".format(batch_id)
    name = "BatchInput{}".format(batch_id)
    fields = {}

    for i, (field_title, field_type, field_params) in enumerate(x(from_table)):
        if field_title == "index":
            field_params.update({'primary_key': True})
            fname = "index"
        else:
            fname = "c{}".format(i)
        fcls = getattr(models, field_type)
        fields[fname] = fcls(db_column=field_title, **field_params)

    from collections import OrderedDict
    model = create_model(name, fields, app_label='dynamic', module='core.batchs', options={'db_table':'BATCH_INPUT_{}'.format(batch_id)})

    return model



def x(table_name):
    from collections import OrderedDict
    from django.db import connection, models, migrations
    from django.db.migrations.migration import Migration
    from django.db import DEFAULT_DB_ALIAS, connections

    fields = []

    options = {}
    options['database'] = 'default'
    connection = connections[options['database']]

    with connection.cursor() as cursor:
        table_description = connection.introspection.get_table_description(cursor, table_name)

        for row in table_description:
            field_type, field_params, field_notes = get_field_type(connection, row.type_code, row)
            fields.append( (row.name, field_type, field_params) )

        return fields


def get_field_type(connection, table_name, row):
    """
    Given the database connection, the table name, and the cursor row
    description, this routine will return the given field type name, as
    well as any additional keyword parameters and notes for the field.
    """
    from collections import OrderedDict

    field_params = OrderedDict()
    field_notes = []

    try:
        field_type = connection.introspection.get_field_type(row.type_code, row)
    except KeyError:
        field_type = 'TextField'
        field_notes.append('This field type is a guess.')

    # This is a hook for data_types_reverse to return a tuple of
    # (field_type, field_params_dict).
    if type(field_type) is tuple:
        field_type, new_params = field_type
        field_params.update(new_params)

    # Add max_length for all CharFields.
    if field_type == 'CharField' and row.internal_size:
        field_params['max_length'] = int(row.internal_size)

    if field_type == 'DecimalField':
        if row.precision is None or row.scale is None:
            field_notes.append(
                'max_digits and decimal_places have been guessed, as this '
                'database handles decimal fields as float')
            field_params['max_digits'] = row.precision if row.precision is not None else 10
            field_params['decimal_places'] = row.scale if row.scale is not None else 5
        else:
            field_params['max_digits'] = row.precision
            field_params['decimal_places'] = row.scale

    return field_type, field_params, field_notes
