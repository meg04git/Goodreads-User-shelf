import re
import pandas as pd
import numpy as np

from bokeh.io import output_notebook, show, curdoc, push_notebook, output_file, curdoc
from bokeh.models import ColumnDataSource, CategoricalColorMapper, LinearInterpolator, TextInput, LabelSet
from bokeh.plotting import figure, output_notebook, show
from bokeh.models.tools import HoverTool
from bokeh.transform import factor_cmap
from bokeh.palettes import Blues8, Set2, GnBu, Spectral6,viridis, all_palettes, small_palettes, brewer, Inferno256, Viridis, magma, Spectral11
from bokeh.palettes import YlOrRd, PuRd, Pastel2,Oranges
from bokeh.layouts import layout, column, row
from bokeh.transform import cumsum

from bokeh.models.widgets import Paragraph
from bokeh.models.widgets import Div

from bokeh.models import ColumnDataSource, Panel
from bokeh.models.widgets import TableColumn, DataTable
from bokeh.layouts import gridplot

from bokeh.models.widgets import Div

def get_stats(lib,dsformat,top10genre):
    
    b1 = lib.num_pages.sort_values(ascending=True)
    shortbook = lib.at[b1.index[0],'Title']
    shortpg = int(lib.at[b1.index[0],'num_pages'])

    b1 = lib.num_pages.sort_values(ascending=False)
    longbook = lib.at[b1.index[0],'Title']
    longpg = int(lib.at[b1.index[0],'num_pages'])
    
    dsformat = lib.pivot_table(lib, index = 'Format', aggfunc={'Id':'count','num_pages':'sum'}).reset_index()
    b1=dsformat.Id.sort_values(ascending=False).index
    fformat = dsformat.Format[b1[0]]
    
    topgenre=top10genre.index[0]
    
    txt = f'<font color="#3B240B"><H2>Lets check out some stats!</H2><br/> You have read <b><font size="3">{len(lib)}</font></b> books till now, a total of ~<b><font size="3">{int(lib.num_pages.sum())}</font></b> pages<br />Your longest book is <b><font size="3">{longbook}</font></b> of <b><font size="3">{longpg}</font></b> pages <br />Your shortest book is <b><font size="3">{shortbook}</font></b> of <b><font size="3">{shortpg}</font></b> pages <br />You mostly read in <b><font size="3">{fformat}</font></b> format <br />Your favourite genre is <b><font size="3">{topgenre}</font></b></font>'

    stats = txt
    return stats

def charts_tab(lib):
#   Default width & height
    w = 500
    h = 300

    # Get unique shelves / genres
#    genrelist = ' '.join(lib.shelves[:]).split()
#    genres = set(genrelist)
#    dict1={}
#    for items in genrelist:
#      dict1[items] = genrelist.count(items)

    # Genres that I read most: Heatmap / Hex ? Genre, count (Filters: All Year)
    lib['shelves'] = lib['shelves'].str.replace('non-fiction', '', case = False)
    lib['shelves'] = lib['shelves'].str.replace('nonfiction', '', case = False)
    lib['shelves'] = lib['shelves'].str.replace('fiction', '', case = False)
    lib.MainGenre = lib.shelves[0]

    for i, x in enumerate(lib.shelves):
#      print('charts tab', x)
      try:
         l = re.findall(r'\w+',x)[0]
         lib.at[i,'MainGenre'] = l
      except:
         lib.at[i,'MainGenre'] = 'no-genre-set'

    top10genre = lib.groupby(by=['MainGenre'], sort=False).count().sort_values(by=['Id'], ascending=False)['Id'][:10]
    top10genrebooks = lib[lib['MainGenre'].isin(top10genre.index)]
    dsgenre = pd.pivot_table(top10genrebooks,index='ReadYear',columns='MainGenre',fill_value=0, aggfunc='count')['Id']

    print('Plotting Stacked Chart started..')
    source=ColumnDataSource(dsgenre)

#    names = list(top10genre.index)
    names = list(dsgenre.columns)
#    print(names)

#-------------
    numlines=len(dsgenre.columns)
    mypalette= Spectral6[0:numlines]
    names = dsgenre.columns
    p = figure(width=w, height=h,
                title="Favourite Genre",
                tooltips = """
                          <div style="width:200px;">
                              @Id
                          </div>
                              """
                )


#####-----
    top10genrelist =list(top10genre.index)
    lib1 = lib[lib['MainGenre'].isin(top10genrelist[:6])]
    top10genrechg = lib1.pivot_table(index='ReadYear',columns='MainGenre',values='Id',aggfunc = 'count',fill_value=0)

    p = figure(
              title="Favourite Genre",
              width= 600, height=400,
              )

    numlines=len(top10genrechg.columns)
    colors_list=Spectral11[0:numlines]
    legends_list = [genre for genre in top10genrechg.columns]

    x = list(top10genrechg.index)
    # for (colr, leg, y ) in zip(colors_list, legends_list, ys):
    for i,colname in enumerate(top10genrechg.columns):
        print(colname)
        y = list(top10genrechg[colname].values)
        p.line(x=x, y=y, 
              color= colors_list[i], 
              legend= legends_list[i],
              line_width = 1.5,
#              line_dash = 'dashed'
              )
        p.circle(x=x, y=y, 
              color= colors_list[i],
              radius = 0.04,
              )
        y1 = [y+0.1 for y in y]
        p.text(x=x, y=y1,
              text= y, #source=ColumnDataSource(dsformat), 
              text_font_size = '8pt', 
              # text_color='color', text_align = 'center'
              )

#####-----

    p.xaxis.visible=True
    p.yaxis.visible=True #False
    p.xaxis.axis_label = 'Genre'
    p.yaxis.axis_label = 'Year'
    p.legend.label_text_font='8pts'
    p.legend.location='top_left'
    # show(p)
    print('Plotting Stacked Chart ended..')

    #[GRAPH] Which format I pefer
    from math import pi

    dsformat = lib.pivot_table(lib, index = 'Format', aggfunc={'Id':'count','num_pages':'sum'}).reset_index()
    dsformat['Perc'] = np.around((dsformat.Id/dsformat.Id.sum())*100)
    dsformat['Angle'] = dsformat.Id/dsformat.Id.sum()*2*pi
    colcount = dsformat.Format.nunique()
    if colcount <=2:
      dsformat['color'] = magma(colcount)
    else:
      dsformat['color'] = Viridis[colcount] 

    p1 = figure(plot_width=w, plot_height=h, 
                title="Book format I've read mostly in",
                tooltips = """
                          <div style="width:200px;">
                              Read @Id books in @Format format | 
                              Read @num_pages pages!
                          </div>
                              """
                )
    p1.vbar(x='index', top='Id', width=0.8, source=ColumnDataSource(dsformat),
            fill_color='color', line_color=None,
            legend = 'Format'
            )
    p1.xaxis.major_label_overrides = {dsformat.index[i]: dsformat.Format[i] for i in range(len(dsformat))}
    p1.text(x='index', y='Id', text= 'Id', source=ColumnDataSource(dsformat), 
            text_font_size = '8pt', text_color='color', text_align = 'center')
    p1.xaxis.axis_label = 'Book Format'
    p1.yaxis.axis_label = 'Count'
   # show(p1)

    # p3 = dsformat.plot.pie(y='Id')
    p2 = figure(plot_width=w, plot_height=h, tooltips="@Format: @Perc%")
    perc = {dsformat.Format[i]:dsformat.Perc[i] for i in range(len(dsformat))}
    p2.wedge(x=0, y=1, radius=0.4,
            start_angle=cumsum('Angle', include_zero=True), end_angle=cumsum('Angle'),
            line_color=None,#"white", 
            fill_color='color', 
            legend='Format', 
            source=dsformat)
    p2.axis.visible = False
#    p2.text(x=0, y=1, text = 'Perc',
#            angle=cumsum('Angle', include_zero=True),
#            source=ColumnDataSource(dsformat),
#            text_font_size = '8pt', text_color='color', text_align = 'center')
    # show(p2)

    # Which languages I read in
    lib.language_code[lib['language_code'].str.contains('en-')]='eng'
    lib['language_code'].unique()

    dslang = lib.pivot_table(lib, index = 'language_code', aggfunc={'Id':'count', 'num_pages':'sum'}).reset_index()
    dslang['Perc'] = np.around((dslang.Id/dslang.Id.sum())*100)
    dslang['Angle'] = dslang.Id/dslang.Id.sum()*2*pi
    colcount = dslang.language_code.nunique()
    if colcount <=2:
      dslang['color'] = magma(colcount)
    else:
      dslang['color'] = Viridis[colcount] 

    print('Plotting format, language preference started..')

    p3 = figure(plot_width=w, plot_height=h, 
                title="Languages I've read",
                tooltips = """ 
                          <div style="width:200px;">
                              @Id books in @language_code language | 
                              Read @num_pages pages!
                          </div>
                              """
                )
    p3.vbar(x='index', top='Id', width=1, source=ColumnDataSource(dslang),
            fill_color='color', line_color=None,
            legend='language_code'
		)

    p3.xaxis.major_label_overrides = {dslang.index[i]: dslang.language_code[i] for i in range(len(dslang))}
    p3.text(x='index', y='Id', text= 'Id', source=ColumnDataSource(dslang), 
            text_font_size = '8pt', text_color='color', text_align = 'center')
    p3.xaxis.axis_label = 'Language'
    p3.yaxis.axis_label = 'Count'
    # show(p1)

#####
    p4 = figure(plot_width=w, plot_height=h, tooltips="@language_code: @Perc%")
    perc = {dslang.language_code[i]:dslang.Perc[i] for i in range(len(dslang))}
    p4.wedge(x=0, y=1, radius=0.4,
            start_angle=cumsum('Angle', include_zero=True), end_angle=cumsum('Angle'),
            line_color=None,#"white", 
            fill_color='color', 
            legend='language_code', 
            source=dslang)
    p4.axis.visible = False
#    p4.text(x=0, y=1, text = 'Perc',source=ColumnDataSource(dslang), 
#            angle=cumsum('Angle', include_zero=True),
#            text_font_size = '8pt', text_color='color', text_align = 'center')
#    # show(p2)

#####
    print('Plotting format, language preference ended..')

# Text

    stats = get_stats(lib,dsformat,top10genre)
    txt = Div(text=stats, width=400, height = h)

    # grid = gridplot([[s1, s2], [None, s3]], plot_width=250, plot_height=250)
    row1 = row(p, txt)
    row2 = row(p1, p2)
    row3 = row(p3, p4)
    layout = column(row1, row2, row3)
    tab = Panel(child = layout, title = 'Trends')

    return tab, dsgenre