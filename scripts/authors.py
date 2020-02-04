# Authors word cloud
from __future__ import division
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from bokeh.palettes import Spectral

from bokeh.models import ColumnDataSource, Panel
from bokeh.models.widgets import TableColumn, DataTable
from bokeh.layouts import layout, column, row

from os.path import dirname, join

def authors_tab(lib, userid):
    print('Plotting Authors wordcloud started..')

    authorlist = ' '.join(lib.Author[:])
#    authorlist
    matp = plt.figure(facecolor = None, frameon=True, edgecolor='green', 
                      figsize = (15,5))

    wordcloud = WordCloud(background_color = 'white', 
                          colormap = 'RdPu', # 'inferno', #'viridis', #colorpalette,
                          width = 1200, height = 500, 
                          relative_scaling='auto').generate(authorlist)
    
    plt.imshow(wordcloud, interpolation='bilinear', 
              )
    plt.axis("off")

    ufile = join(dirname(__file__), '../data', f'{userid}authorcloud.png')
    plt.savefig(ufile) #Read this image in bokeh

    import numpy as np
    from PIL import Image
    from bokeh.plotting import figure, show, output_file

#-----------------
    # Open image, and make sure it's RGB*A*
    lena_img = Image.open(ufile).convert('RGBA')
    xdim, ydim = lena_img.size
    print("Dimensions: ({xdim}, {ydim})".format(**locals()))
    # Create an array representation for the image `img`, and an 8-bit "4
    # layer/RGBA" version of it `view`.
    img = np.empty((ydim, xdim), dtype=np.uint32)
    view = img.view(dtype=np.uint8).reshape((ydim, xdim, 4))
    # Copy the RGBA image into view, flipping it so it comes right-side up
    # with a lower-left origin
    view[:,:,:] = np.flipud(np.asarray(lena_img))

    # Display the 32-bit RGBA image
    dim = max(xdim, ydim)
    fig = figure(
#                title="Lena",
                x_range=(0,xdim), y_range=(0,ydim),
                # Specifying xdim/ydim isn't quire right :-(
#                width=xdim, height=ydim,
                width=1200, #height=300,
                )
    fig.image_rgba(image=[img], x=0, y=0, dw=xdim, dh=ydim)
    fig.axis.visible = False
#    output_file("lena.html", title="image example")
#    show(fig)
#-----------------

    layout = row(fig)
    tab = Panel(child = layout, title = 'Favourite Authors')

    print('Plotting Authors wordcloud ended..')

    return tab