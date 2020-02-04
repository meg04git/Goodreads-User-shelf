# -*- coding: utf-8 -*-
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pickle
import statistics 
import re
import requests
from bs4 import BeautifulSoup
import time
from os.path import dirname, join

import warnings
warnings.filterwarnings("ignore")

# Load User books
from bokeh.io import output_notebook, show, curdoc, push_notebook, output_file, curdoc
from bokeh.models import ColumnDataSource, CategoricalColorMapper, LinearInterpolator, TextInput, LabelSet
from bokeh.plotting import figure, output_notebook, show
from bokeh.models.tools import HoverTool
from bokeh.transform import factor_cmap
from bokeh.palettes import Blues8, Set2, GnBu, Spectral6,viridis, all_palettes, small_palettes, brewer, Inferno256, Viridis
from bokeh.palettes import YlOrRd, PuRd, Pastel2,Oranges
from bokeh.layouts import layout, column, row
from bokeh.transform import cumsum
from bokeh.models.widgets import Div

# os methods for manipulating paths
from os.path import dirname, join, basename

# Bokeh basics 
from bokeh.io import curdoc
from bokeh.models.widgets import Tabs, Panel

# Each tab is drawn by one script
from scripts.bookshelf import bookshelf_tab
from scripts.authors import authors_tab
from scripts.charts import charts_tab
from scripts.genre import genre_tab
from scripts.extractdata import handle_submit_details

color = 'viridis' 
# color = small_palettes['Pastel2']
# colorpalette = 'Pastel2'
font = "Lucida Handwriting"

lib=pd.DataFrame()

def handle_userid(attr, old, new):
  wuserid.value = wuserid.value.strip()
  txt.text = ''
  success = True
  if cb_group.active == []: #Clear buffer checkbox is not selected then read local file
    try:
      ufile = join(dirname(__file__), 'data', f'{wuserid.value}UserLibrary.csv')
      print('Reading local file', ufile)
      success = True
      lib = pd.read_csv(ufile)
      if lib.empty == True:
        print('File is empty, extracting data from GR')
        success = False
    except: #Failed reading file
      print('Error reading local file, extracting data from GR')
      success = False
  else:
    print('User selected clearing of buffer. Extracting data from GR')
    success=False
  if success == False:  
    lib, success = handle_submit_details(wuserid)
# Create each of the tabs
  print('success=', success)
  if success == True:
    print('Entered tab if')
    tab1 = bookshelf_tab(lib)
    tab2 = authors_tab(lib, wuserid.value)
    tab3, dsgenre = charts_tab(lib)
#    tab4 = genre_tab(dsgenre)
#    tab0 = wuserid
# Put all the tabs into one application
    tabs = Tabs(tabs = [tab3, tab2, tab1])

    print('completed tab')

#   Remove Text & Clear buffer button
    try:
      c1.children.remove(txt)
      c1.children.remove(cb_group)
    except:
      pass

# Put the tabs in the current document for display
    curdoc().add_root(tabs)
    print('completed cursor')

# Get User id
from bokeh.models.widgets import TextInput, CheckboxGroup
wuserid = TextInput(value="", title="Goodreads Read shelf id:")

wuserid.on_change('value', handle_userid) # Extract data

#url = join(dirname(__file__), "static", "books-transparent-background-13.png")
#url = join(basename(dirname(__file__)), "static", "books-transparent-background-13.png")
#div = Div(text="<img src='https://faithhogan.com/wp-content/uploads/2016/03/Books-banner.png' width=600, height=60>")

src = 'http://i.huffpost.com/gen/919298/images/o-GOODREADS-SELL-BOOKS-facebook.jpg'
div = Div(text="<img src='http://i.huffpost.com/gen/919298/images/o-GOODREADS-SELL-BOOKS-facebook.jpg' width=900, height=200>")

from bokeh.models.widgets import Paragraph
txt = Div(text="""Enter id & press Enter. Click on Read shelf in myBooks, shelf id can be found between "/" & "?". This will take a while if running for first time, Take a break...""",
width=400, height=100)

cb_group = CheckboxGroup(labels=["Clear buffer"]) #, active=[0])

c1 = column(cb_group, txt)
r1 = row(wuserid, c1)
layout = column(div, r1)

from bokeh.plotting import figure, curdoc
from bokeh.models import ColumnDataSource, Range1d

# Put the tabs in the current document for display
curdoc().add_root(layout)