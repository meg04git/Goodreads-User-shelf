import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import statistics 
import time
import warnings
warnings.filterwarnings("ignore")

from bokeh.models import ColumnDataSource, Panel
from bokeh.models.widgets import TableColumn, DataTable
from bokeh.models.widgets import Div

def bookshelf_tab(lib):

    from bokeh.io import output_notebook, show, curdoc, push_notebook, output_file, curdoc
    # from bokeh.io import hplot
    from bokeh.models import ColumnDataSource, CategoricalColorMapper, LinearInterpolator, TextInput, LabelSet
    from bokeh.plotting import figure, output_notebook, show
    from bokeh.models.tools import HoverTool
    from bokeh.transform import factor_cmap
    from bokeh.palettes import Blues8, Set2, GnBu, Spectral6,viridis, all_palettes, small_palettes, brewer, Inferno256, Viridis
    from bokeh.palettes import YlOrRd, PuRd, Pastel2,Oranges
    from bokeh.layouts import layout, column, row
    from bokeh.transform import cumsum

    color = 'viridis' 
    # color = small_palettes['Pastel2']
    # colorpalette = 'Pastel2'
    font = "Lucida Handwriting"

    """### [GRAPH] bookshelf poster"""

    # My Reading graph: Number of books I have read over the years (graph): Total, genre
    rating = list(lib.Rating.unique())
    rating = list(str(x) for x in rating)
    lib.num_pages.max()

    # output_file(path/"p.html")

    source1 = ColumnDataSource(lib)
    p = figure(
        plot_width=600, plot_height=900, 
              #  x_range = (2010, 2020),
              #  y_range = (10,70),
              title="My Bookshelf Frame"
    )
    # p.yaxis.axis_label = 'Number of books read'
    size_mapper = LinearInterpolator(
        # x = [0,5], #Min Max Rating 
        x = [lib.num_pages.min(), lib.num_pages.max()],
        y = [10,100]
    )

    # rating = lib.Rating.unique()
    color_mapper = CategoricalColorMapper(
        # factors = [str(x) for x in lib.Rating.unique()],
        # factors = ['5', '4', '3', '2', '1', '0'],
        # palette = ['#000003', '#410967', '#932567', '#DC5039', '#FBA40A', '#FCFEA4'],
        factors = list(lib.Format.unique()),
        palette = viridis(lib.Format.nunique()), #small_palettes['Viridis'][4], #['#30678D', '#35B778'],
        )

    # Parameter
    kwargs = dict(x = 'ReadYear',  
          y = 'index',
          line_color = 'coral',
          fill_alpha = 0.5,
          size = {'field':'num_pages', 'transform':size_mapper},
          #  color = {'field':'Rating', 'transform':color_mapper},
          fill_color = {'field':'Format', 'transform':color_mapper},
#          legend_group='Format',
    )

    print('Plotting 1 started..')
    # Hardcover
    cds_format = lib[lib['Format']=='Hardcover']
    p.hex(source = ColumnDataSource(cds_format),
          legend = 'Hardcover',
          **kwargs,) 

    # Paperback
    cds_paperback = lib[lib['Format']=='Paperback']
    p.diamond(source = ColumnDataSource(cds_paperback),
          legend = 'Paperback',
          **kwargs,) 

    # Audio
    cds_audio = lib[lib['Format']=='Audio']
    p.triangle(source = ColumnDataSource(cds_audio),
          legend = 'Audio',
          **kwargs,) 

    # ebook
    cds_ebook = lib[lib['Format']=='ebook']
    p.inverted_triangle(source = ColumnDataSource(cds_ebook),
          legend = 'Ebook',
          **kwargs,) 

    # Series
    cds_series = lib[lib['series_work']==True]
    p.circle_cross(source = ColumnDataSource(cds_series),
          size = 10,
          legend = 'Series',
          x = 'ReadYear',  
          y = 'index',
          line_color = 'white', 
          fill_alpha = 0.5,
    ) 

    # # Ratings
    # p.dash(source = ColumnDataSource(lib[lib['Rating']==5]),
    #        size = 20,
    #        legend = 'Rating',
    #        x = 'ReadYear', 
    #        y = 'index',
    #        line_color = 'crimson', #''aqua', 'aquamarine', 'brown', 'burlywood', 'cadetblue', 'chartreuse', 
    # 'chocolate', 'coral', 'cornflowerblue', 'cornsilk', 'crimson', 'cyan', 'darkblue', 'darkcyan', 'darkgoldenrod', 
    # 'darkgray', 'darkgreen', 'darkgrey', 'darkkhaki', 'darkmagenta', 'darkolivegreen', 'darkorange', 'darkorchid', 
    # 'darkred', 'darksalmon', 'darks
    #        fill_alpha = 0.5,
    # ) 

                            # <div>
                            #     <img
                            #         src="@ImgURL" height="42" alt="@imgs" width="42"
                            #         style="float: left; margin: 0px 15px 15px 0px;"
                            #         border="2"
                            #     ></img>
                            # </div> 

    p.text(x='ReadYear', y=len(lib), source=cds_format,
          text='ReadYear', text_align = 'center', 
          text_font = font, text_font_size = '15pt', text_alpha = 0.2, 
          angle=0,
          text_color = 'crimson',)
                              
    hover = HoverTool(show_arrow = False)
    # <div style ="border-style: solid;border-width: 15px;background-color:black;"> 
    hover.tooltips = """<div style ="float: left;">    
                            <div>
                                <img
                                    src="@ImgURL"
                                ></img>
                            </div>     
                            <div>
                              <span style="font-size: 12px; color: crimson;font-family:arial;font-weight: bold;">@Title</span>
                              <span style="font-size: 10px; color: crimson;font-family:arial;">
                              <div>
                                @Format | 
                                @num_pages pages |
                                Rated @Rating stars</span>
                              </div>
                            </div>
                          </div>
                      """
                      
    p.legend.location = (-1,1)
    # p.add_layout(legend, 'right')
    p.title.text_font = "Lucida Handwriting"
    p.title.text_font_style = 'bold italic'
    p.title.text_font_size = '12pt'
    p.yaxis.visible = False
    p.legend.label_text_font_style = 'italic'
    p.legend.label_text_font_size = '10pt'
    p.legend.label_text_font = "Lucida Handwriting"
    p.add_tools(hover)
    show(p) #, notebook_handle=True)
    print('Plotting 1 ended..')
    
    div = Div(text= """<font color="#3B240B"><H3>Your bookshelf Frame</H3>Type of every book you've read is plotted in different shapes. Check out the legend for the shape associated with the type. Size of the shape indicates the length of the book. Longer the book, bigger the shape. Crossed circles are the series from your read shelf.<br /><br />Hover over the shapes to find out the book it represents. You can also download and share it!</font>""", width = 350)
    layout = row(p, div)
    tab = Panel(child = layout, title = 'Bookshelf')

    return tab