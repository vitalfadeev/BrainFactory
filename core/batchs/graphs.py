import plotly.express as px
import plotly.offline as opy
from . import models


def get_colorset(colorset):
    if colorset == "1":
        color_continuous_scale = px.colors.qualitative.Light24
    elif colorset == "2":
        color_continuous_scale = px.colors.qualitative.Pastel1
    elif colorset == "3":
        color_continuous_scale = px.colors.qualitative.Bold
    elif colorset == "4":
        color_continuous_scale = px.colors.sequential.Inferno
    elif colorset == "5":
        color_continuous_scale = px.colors.sequential.GnBu
    elif colorset == "6":
        color_continuous_scale = px.colors.sequential.OrRd
    elif colorset == "7":
        color_continuous_scale = px.colors.sequential.amp
    elif colorset == "8":
        color_continuous_scale = px.colors.sequential.ice
    elif colorset == "9":
        color_continuous_scale = px.colors.colorbrewer.RdBu
    elif colorset == "10":
        color_continuous_scale = px.colors.sequential.PuBu
    elif colorset == "11":
        color_continuous_scale = px.colors.sequential.Reds
    else:
        color_continuous_scale = px.colors.qualitative.Light24

    return color_continuous_scale


def g1(batch_id, x, y, color, colorset):
    input_model = models.BatchInput(batch_id)
    df = input_model.as_pandas_dataframe()

    fig = px.scatter(df, x=x, y=y, color=color,
        color_continuous_scale=get_colorset(colorset))
    div = opy.plot(fig, auto_open=False, output_type='div')

    return div


def g2(batch_id, x, y, color, colorset):
    input_model = models.BatchInput(batch_id)
    df = input_model.as_pandas_dataframe()

    fig = px.scatter(df, x=x, y=y, color=color, marginal_y="rug", marginal_x="histogram",
        color_continuous_scale=get_colorset(colorset))
    div = opy.plot(fig, auto_open=False, output_type='div')

    return div


def g3(batch_id, x, y, color, colorset):
    input_model = models.BatchInput(batch_id)
    df = input_model.as_pandas_dataframe()

    fig = px.scatter(df, x=x, y=y, color=color, marginal_y="violin", marginal_x="box", trendline="ols",
        color_continuous_scale=get_colorset(colorset))
    div = opy.plot(fig, auto_open=False, output_type='div')

    return div


def g4(batch_id, x, y, z, color, colorset):
    input_model = models.BatchInput(batch_id)
    df = input_model.as_pandas_dataframe()

    fig = px.scatter_matrix(df, dimensions=[x, y, z], color=color,
        color_continuous_scale=get_colorset(colorset))
    div = opy.plot(fig, auto_open=False, output_type='div')

    return div


def g5(batch_id, color, colorset):
    input_model = models.BatchInput(batch_id)
    df = input_model.as_pandas_dataframe()

    fig = px.parallel_categories(df, color=color,
        color_continuous_scale=get_colorset(colorset))
    div = opy.plot(fig, auto_open=False, output_type='div')

    return div


def g6(batch_id, x, y, color, line_group, colorset):
    input_model = models.BatchInput(batch_id)
    df = input_model.as_pandas_dataframe()

    # sorting data frame by name
    #df.sort_values(line_group, axis=0, ascending=True, inplace=True, na_position='last')

    fig = px.area(df, x=x, y=y, color=color, line_group=line_group,
        color_discrete_sequence=get_colorset(colorset))
    div = opy.plot(fig, auto_open=False, output_type='div')

    return div


def g7(batch_id, x, y, colorset):
    input_model = models.BatchInput(batch_id)
    df = input_model.as_pandas_dataframe()

    fig = px.density_contour(df, x=x, y=y)
    div = opy.plot(fig, auto_open=False, output_type='div')

    return div


def g8(batch_id, x, y, colorset):
    input_model = models.BatchInput(batch_id)
    df = input_model.as_pandas_dataframe()

    fig = px.density_heatmap(df, x=x, y=y, marginal_x="rug", marginal_y="histogram",
        color_continuous_scale=get_colorset(colorset))
    div = opy.plot(fig, auto_open=False, output_type='div')

    return div


def g9(batch_id, x, y, color, colorset):
    input_model = models.BatchInput(batch_id)
    df = input_model.as_pandas_dataframe()

    fig = px.histogram(df, x=x, y=y, color=color, marginal="rug", hover_data=[x, y, color],
        color_discrete_sequence=get_colorset(colorset))
    div = opy.plot(fig, auto_open=False, output_type='div')

    return div


def g10(batch_id, x, y, z, color, colorset):
    input_model = models.BatchInput(batch_id)
    df = input_model.as_pandas_dataframe()

    fig = px.scatter_3d(df, x=x, y=y, z=z, color=color,
        color_discrete_map={"Joly": "blue", "Bergeron": "green", "Coderre": "red"},
        color_continuous_scale=get_colorset(colorset))
    div = opy.plot(fig, auto_open=False, output_type='div')

    return div


