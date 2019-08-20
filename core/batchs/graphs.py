from . import models


def g1(batch_id, x, y, color):
    import plotly.express as px
    import plotly.offline as opy

    input_model = models.BatchInput(batch_id)
    df = input_model.as_pandas_dataframe()

    fig = px.scatter(df, x=x, y=y, color=color)
    div = opy.plot(fig, auto_open=False, output_type='div')

    return div


def g2(batch_id, x, y, color):
    import plotly.express as px
    import plotly.offline as opy

    input_model = models.BatchInput(batch_id)
    df = input_model.as_pandas_dataframe()

    fig = px.scatter(df, x=x, y=y, color=color, marginal_y="rug", marginal_x="histogram")
    div = opy.plot(fig, auto_open=False, output_type='div')

    return div


def g3(batch_id, x, y, color):
    import plotly.express as px
    import plotly.offline as opy

    input_model = models.BatchInput(batch_id)
    df = input_model.as_pandas_dataframe()

    fig = px.scatter(df, x=x, y=y, color=color, marginal_y="violin", marginal_x="box", trendline="ols")
    div = opy.plot(fig, auto_open=False, output_type='div')

    return div


def g4(batch_id, x, y, z, color):
    import plotly.express as px
    import plotly.offline as opy

    input_model = models.BatchInput(batch_id)
    df = input_model.as_pandas_dataframe()

    fig = px.scatter_matrix(df, dimensions=[x, y, z], color=color)
    div = opy.plot(fig, auto_open=False, output_type='div')

    return div


def g5(batch_id, color):
    import plotly.express as px
    import plotly.offline as opy

    input_model = models.BatchInput(batch_id)
    df = input_model.as_pandas_dataframe()

    fig = px.parallel_categories(df, color=color, color_continuous_scale=px.colors.sequential.Inferno)
    div = opy.plot(fig, auto_open=False, output_type='div')

    return div


def g6(batch_id, x, y, color, line_group):
    import plotly.express as px
    import plotly.offline as opy

    input_model = models.BatchInput(batch_id)
    df = input_model.as_pandas_dataframe()

    # sorting data frame by name
    df.sort_values(line_group, axis=0, ascending=True, inplace=True, na_position='last')

    fig = px.area(df, x=x, y=y, color=color, line_group=line_group)
    div = opy.plot(fig, auto_open=False, output_type='div')

    return div


def g7(batch_id, x, y):
    import plotly.express as px
    import plotly.offline as opy

    input_model = models.BatchInput(batch_id)
    df = input_model.as_pandas_dataframe()

    fig = px.density_contour(df, x=x, y=y)
    div = opy.plot(fig, auto_open=False, output_type='div')

    return div


def g8(batch_id, x, y):
    import plotly.express as px
    import plotly.offline as opy

    input_model = models.BatchInput(batch_id)
    df = input_model.as_pandas_dataframe()

    fig = px.density_heatmap(df, x=x, y=y, marginal_x="rug", marginal_y="histogram")
    div = opy.plot(fig, auto_open=False, output_type='div')

    return div


def g9(batch_id, x, y, color):
    import plotly.express as px
    import plotly.offline as opy

    input_model = models.BatchInput(batch_id)
    df = input_model.as_pandas_dataframe()

    fig = px.histogram(df, x=x, y=y, color=color, marginal="rug", hover_data=[x, y, color])
    div = opy.plot(fig, auto_open=False, output_type='div')

    return div


def g10(batch_id, x, y, z, color):
    import plotly.express as px
    import plotly.offline as opy

    input_model = models.BatchInput(batch_id)
    df = input_model.as_pandas_dataframe()

    fig = px.scatter_3d(df, x=x, y=y, z=z, color=color,
        color_discrete_map={"Joly": "blue", "Bergeron": "green", "Coderre": "red"})
    div = opy.plot(fig, auto_open=False, output_type='div')

    return div


