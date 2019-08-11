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
