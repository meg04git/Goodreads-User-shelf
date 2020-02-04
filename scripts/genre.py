# Genre Heatmap
from __future__ import division
import seaborn as sns
from bokeh.palettes import Spectral

from bokeh.models import ColumnDataSource, Panel
from bokeh.models.widgets import TableColumn, DataTable
from bokeh.layouts import layout, column, row
from bokeh.palettes import Blues8, Set2, GnBu, Spectral6,viridis, all_palettes
from bokeh.plotting import figure

def genre_tab(dsgenre):

    numlines=len(dsgenre.columns)
    mypalette= Spectral6[0:numlines]

    fig = figure(width=500, height=300,
                title="Genre",
                )
    fig.multi_line(
                    xs=[dsgenre.index.values]*numlines,
                    ys=[dsgenre[name].values for name in dsgenre.columns],
                    line_color=mypalette,
                    line_width=5)
#    show(fig)
    layout = row(fig)
    tab = Panel(child = layout, title = 'Genre')

    print('Plotting Genre Heatmap ended..')

    return tab