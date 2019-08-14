from django.apps import apps
from django.db import models
from django.db.backends.sqlite3.operations import DatabaseOperations


# fix sqlite3 column quoting: "age" -> `"age"`
def quote_name_fixed(self, name):
    if name.startswith('`') and name.endswith('`'):
        return name  # Quoting once is enough.
    return '`%s`' % name
setattr(DatabaseOperations, 'quote_name', quote_name_fixed)


class DymoMixin:
    @classmethod
    def get_column_names(cls, without_pk=False):
        titles = []
        for field in cls._meta.get_fields():
            if without_pk:
                if field.primary_key:
                    pass
                else:
                    titles.append(field.db_column.strip('`'))
            else:
                titles.append(field.db_column.strip('`'))
        return titles


#
# Dynamic model
#
def create_model(base_classes, name, fields=None, app_label='', module='', options=None):
    """
    Create specified model
    example:
      model = create_model(name, fields, app_label='dynamic', module='core.batchs', options={'db_table':'BATCH_INPUT_{}'.format(batch_id)})
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
    model = type(name, base_classes, attrs)

    return model


def get_db_table_fields(table_name):
    """
    Return fields from DB table.
    It read DB structure and return fields.
    """
    from django.db import connections

    fields = []

    options = {}
    options['database'] = 'default'
    connection = connections[options['database']]

    with connection.cursor() as cursor:
        # table & fields
        table_description = connection.introspection.get_table_description(cursor, table_name)
        # pk
        primary_key_column = connection.introspection.get_primary_key_column(cursor, table_name)
        # unique
        constraints = {}

        unique_columns = [
            c['columns'][0]
                for c in constraints.values()
                    if c['unique'] and len(c['columns']) == 1
        ]

        for row in table_description:
            column_name = row.name
            field_type, field_params, field_notes = get_field_type(connection, row)

            # Add primary_key and unique, if necessary.
            if column_name == primary_key_column:
                field_params['primary_key'] = True
            elif column_name in unique_columns:
                field_params['unique'] = True

            fields.append( (row.name, field_type, field_params) )

        return fields


def get_field_type(connection, row):
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


def get_dynamic_model(base_classes, class_name, from_table, app_label, module_name, primary_key_column):
    """
    Dynamic Django Model factory
    - create model
    - read table structure from DB
    - auto append fields to model
    - fields names: c0, c1, c2, ..., cN
    example:
        class_name = "BatchInput{}".format(batch_id)
        from_table = "BATCH_INPUT_{}".format(batch_id)
        model = get_dynamic_model(class_name, from_table, pk_field, 'dynamic', 'core.batchs')
    """
    fields = {}

    # add fields
    for i, (field_title, field_type, field_params) in enumerate(get_db_table_fields(from_table)):
        fname = "c{}".format(i)

        # wrap to `...`. for columns with spaces, like "The name" -> `"The name"`
        field_params['db_column'] = '`' + field_title + '`'

        # pk
        if field_title == primary_key_column:
            field_params['primary_key'] = True

        # types: ChatField(), IntegerField(), BigIntegerField(), DateTimeField()
        fcls = getattr(models, field_type)

        # field instance
        fields[fname] = fcls(**field_params)

    # check exists
    try:
        # exist
        model = apps.get_model(app_label, class_name)
    except LookupError:
        # create
        model = create_model(base_classes, class_name, fields, app_label=app_label, module=module_name, options={'db_table':from_table})

    return model

