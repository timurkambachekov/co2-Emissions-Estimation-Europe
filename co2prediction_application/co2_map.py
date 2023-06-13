import pickle
import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from shapely.geometry import box
from sklearn.metrics import mean_absolute_error

matplotlib.use("TkAgg")


def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side="top", fill="both", expand=0)
    plt.tight_layout()
    return figure_canvas_agg


def delete_figure_agg(figure_agg):
    figure_agg.get_tk_widget().forget()
    try:
        draw_figure.canvas_packed.pop(figure_agg.get_tk_widget())
    except Exception as e:
        print(f'Error removing {figure_agg} from list', e)
    plt.close('all')


def get_data(year: int, month: int,):
    def condition(df, X): return df[(X['Year'] == year) & (X['Month'] == month)]

    # with open('/Users/timurkambachekov/вышка/3 курс/Проект 3 курс/code/model_selection/model.pkl', 'rb') as f:
    #     gbr = pickle.load(f)

    with open('/Users/timurkambachekov/вышка/3 курс/Проект 3 курс/code/model_selection/rf.pkl', 'rb') as f:
        rf = pickle.load(f)

    X_trans = pd.read_pickle('/Users/timurkambachekov/вышка/3 курс/Проект 3 курс/code/model_selection/X_trans.pkl')
    X = pd.read_pickle('/Users/timurkambachekov/вышка/3 курс/Проект 3 курс/code/model_selection/X.pkl')
    y = pd.read_pickle('/Users/timurkambachekov/вышка/3 курс/Проект 3 курс/code/model_selection/y.pkl')

    X_trans, X, y = condition(X_trans, X), condition(X, X), condition(y, X)
    # y_pred = gbr.predict(X_trans).squeeze()
    y_pred = rf.predict(X)

    # mae = np.round(gbr.evaluate(X_trans, y)[1], 5)
    # preds = pd.merge(X.reset_index(), pd.Series(y_pred, name='Emissions'), left_index=True, right_index=True).drop(
    #     columns=['index'])

    mae = np.round(mean_absolute_error(y, y_pred), 5)
    preds = pd.merge(X.reset_index(drop=True), pd.Series(y_pred, name='Emissions'), left_index=True, right_index=True)
    preds['Diff'] = np.abs(preds['Emissions'] - y.reset_index(drop=True))
    gdf = gpd.GeoDataFrame(
        preds, geometry=gpd.points_from_xy(x=preds.Longitude, y=preds.Latitude)
    )

    return gdf, mae


def plot_emission_map(gdf: gpd.GeoDataFrame, quantiles: int):
    fig_size = (12, 5)
    fig, ax = plt.subplots(figsize=fig_size)

    world_filepath = gpd.datasets.get_path('naturalearth_lowres')
    world = gpd.read_file(world_filepath)
    europe = gpd.clip(world, box(-25, 35, 65, 72))

    europe.boundary.plot(
        figsize=fig_size,
        ax=ax,
        color='black'
    )
    gdf.plot(
        'Emissions',
        ax=ax,
        scheme='quantiles',
        k=quantiles,
        figsize=fig_size,
        marker='s',
        markersize=50,
        legend=True, legend_kwds={'bbox_to_anchor': (1, 1)}
    )
    plt.axis('off')
    plt.title('CO2 Emissions (Europe), gC/m2/day')

    return fig


def plot_emission_diff_map(gdf: gpd.GeoDataFrame):
    fig_size = (12, 5)
    fig, ax = plt.subplots(figsize=fig_size)

    world_filepath = gpd.datasets.get_path('naturalearth_lowres')
    world = gpd.read_file(world_filepath)
    europe = gpd.clip(world, box(-25, 35, 65, 72))

    europe.boundary.plot(
        figsize=fig_size,
        ax=ax,
        color='black'
    )
    gdf.plot(
        'Diff',
        ax=ax,
        cmap='OrRd',
        figsize=fig_size,
        marker='s',
        markersize=40,
        legend=True
    )
    plt.axis('off')
    plt.title('CO2 Emissions Prediction Error (Europe), gC/m2/day')

    return fig