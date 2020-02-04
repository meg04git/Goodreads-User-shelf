import requests
import re, time
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import statistics
import collections
#from collections import Counter

import warnings
warnings.filterwarnings("ignore")

# os methods for manipulating paths
from os.path import dirname, join

# Get Book master for user books
# For each book in books, get its author, genre, rating count, setting, literary awards, quotes, trivia, listopia

bookcolumns = (['Id','Title','ISBN','Author', 'publication_year','publisher',
                'language_code','description','reviews_count','ratings_count',
                'original_publication_year','num_pages','format','series_work',
                'similar_books','shelves','SmallImgURL','ImgURL'])
#               ,'Setting', 'Awards'])


def get_booksoup(book): 
  parameters = {
                'format': 'xml', # or json
                'id': book, #A Goodreads internal book_id
                # text_only: Only show reviews that have text (default false)
                # rating: Show only reviews with a particular rating (optional)
                'key': 'hBFAWIoikCpkWn2JEjXyQ'   #Developer key (required).
                }
  url = 'https://www.goodreads.com/book/show/'

  bookresponse = requests.get(url, params=parameters)
  booksoup = BeautifulSoup(bookresponse.content, 'xml') 
  return booksoup

def get_bookmaster(id, booksoup):
  bookdb=[]
  bookdb=pd.DataFrame(columns=bookcolumns)
  i=0
  bookdb.at[i,'Id'] = booksoup.find_all(name = 'id')[0].get_text(strip = True)
  bookdb.at[i,'Title'] = booksoup.find_all(name = 'title')[0].get_text(strip = True)
  bookdb.at[i,'ISBN'] = booksoup.find_all(name = 'isbn')[0].get_text(strip = True)
  bookdb.at[i,'Author'] = booksoup.find_all(name = 'name')[0].get_text(strip = True)
  bookdb.at[i,'publication_year'] = booksoup.find_all(name = 'publication_year')[0].get_text(strip = True)
  bookdb.at[i,'publisher'] = booksoup.find_all(name = 'publisher')[0].get_text(strip = True)
  bookdb.at[i,'language_code'] = booksoup.find_all(name = 'language_code')[0].get_text(strip = True)
  bookdb.at[i,'description'] = booksoup.find_all(name = 'description')[0].get_text(strip = True)
  bookdb.at[i,'reviews_count'] = booksoup.find_all(name = 'text_reviews_count')[0].get_text(strip = True)
  bookdb.at[i,'ratings_count'] = booksoup.find_all(name = 'ratings_count')[0].get_text(strip = True)
  bookdb.at[i,'original_publication_year'] = booksoup.find_all(name = 'original_publication_year')[0].get_text(strip = True)
  bookdb.at[i,'num_pages'] = booksoup.find_all(name = 'num_pages')[0].get_text(strip = True)
  bookdb.at[i,'format'] = booksoup.find_all(name = 'format')[0].get_text(strip = True)
  bookdb.at[i,'SmallImgURL'] = booksoup.find_all(name = 'small_image_url')[0].get_text(strip = True)
  bookdb.at[i,'ImgURL'] = booksoup.find_all(name = 'image_url')[0].get_text(strip = True)
  
  try:
    series = booksoup.find_all(name = 'series_work')[0].get_text(strip = True)
    bookdb.at[0,'series_work'] = True
  except:
    bookdb.at[0,'series_work'] = False
  try:
    similar = booksoup.find_all(name = 'similar_books')[0] #.get_text(strip = True)
    similarbooks = similar.find_all(name = 'title')
    bookdb.at[0,'similar_books'] = ';'.join(list(map(lambda x: x.get_text(strip = True),similarbooks)))
  except:
    bookdb.at[0,'similar_books'] = 'None'
  # bookdb.at[i,'Setting'] = booksoup.find_all(name = 'Setting')[0].get_text(strip = True)
  # bookdb.at[i,'Awards'] = booksoup.find_all(name = 'award-winners')[0].get_text(strip = True)
  bookdb.at[i,'shelves'] = get_top10genre(booksoup)
  return bookdb

def get_top10genre(booksoup):
  totshelf = booksoup.find_all(name = 'shelf')
  shelflist=[]
  i=0
  for x in totshelf:
    f = re.findall(r'\"(.*?)\"', str(x))
    if f[1] not in ['to-read','currently-reading','Read','All','Want to Read']:
      shelflist.append(f[1])
      i+=1
    if i >= 10:
      break
  shelf = ' '.join(shelflist)
  return shelf

def _counts(data):
    """Return a count collection with the highest frequency.
    >>> _counts([1, 1, 2, 3, 3, 3, 3, 4])     [(3, 4)]
    >>> _counts([2.75, 1.75, 1.25, 0.25, 0.5, 1.25, 3.5])     [(1.25, 2)]
    """
    table = collections.Counter(iter(data)).most_common()
    if not table:
        return table
    maxfreq = table[0][1]
    for i in range(1, len(table)):
        if table[i][1] != maxfreq:
            table = table[:i]
            break
    return table

def mode(data):
    # Return the most common data point from discrete or nominal data.
    
    data_len = len(data)
    if data_len == 0:
        raise StatisticsError('no mode for empty data')
    table = _counts(data)
    table_len = len(table)
    print(table)
    # if table_len != 1:
    #     raise StatisticsError(
    #         'no unique mode; found %d equally common values' % table_len
    #     )
    return table[0][0]

def fix_data(booksdb, wuserid):
  print('Data fixing started')

  booksdb.description.at[booksdb.description.isnull()] = booksdb.Title

  booksdb.publication_year.at[booksdb.publication_year.isnull()] = booksdb.original_publication_year
  booksdb.publication_year.at[booksdb.publication_year==''] = booksdb.original_publication_year

  try:
    booksdb.publication_year.at[booksdb.publication_year.isnull()] = statistics.mode(booksdb[booksdb.publication_year.notnull()].publication_year)
  except:
    booksdb.publication_year.at[booksdb.publication_year.isnull()] = mode(booksdb[booksdb.publication_year.notnull()].publication_year)

  booksdb.ISBN.at[booksdb.ISBN.isnull()] = 'MissingISBN'
  booksdb.ISBN.at[booksdb.ISBN==''] = 'MissingISBN'

  booksdb.publisher.at[booksdb.publisher.isnull()] = 'MissingPublisher'
  booksdb.publisher.at[booksdb.publisher==''] = 'MissingPublisher'

  try:
    booksdb.language_code.at[booksdb.language_code.isnull()] = statistics.mode(booksdb[booksdb.language_code.notnull()].language_code)
  except:
    booksdb.language_code.at[booksdb.language_code.isnull()] = mode(booksdb[booksdb.language_code.notnull()].language_code)

  try:
    booksdb.original_publication_year.at[booksdb.original_publication_year.isnull()] = statistics.mode(booksdb[booksdb['original_publication_year'].notnull()].original_publication_year)
  except:
    booksdb.original_publication_year.at[booksdb.original_publication_year.isnull()] = mode(booksdb[booksdb['original_publication_year'].notnull()].original_publication_year)

  booksdb.num_pages.at[booksdb.num_pages.isnull()] = 0
  booksdb.num_pages.at[booksdb.num_pages == ''] = 0
  booksdb.num_pages.at[booksdb.num_pages == 'nan'] = 0
  booksdb.num_pages = pd.to_numeric(booksdb.num_pages)
  booksdb.num_pages.at[booksdb.num_pages == 0] = np.around(np.average(booksdb.num_pages[booksdb.num_pages.notnull()]))

  try:
    booksdb.format.at[booksdb.format.isnull()] = statistics.mode(booksdb[booksdb['format'].notnull()].format)
  except:
    booksdb.format.at[booksdb.format.isnull()] = mode(booksdb[booksdb['format'].notnull()].format)

  booksdb.shelves.at[booksdb.shelves.isnull()] = 'nogenreset'
  booksdb.shelves.at[booksdb.shelves==''] = 'nogenreset'
  booksdb.shelves.at[booksdb.shelves=='nan'] = 'nogenreset'

# Convert to category
# language_code, format, series_work
  booksdb.language_code = booksdb.language_code.astype('category')
  booksdb.format = booksdb.format.astype('category')
  booksdb.series_work = booksdb.series_work.astype('category')
  
  # Save All user book master
  ufile = join(dirname(__file__), '../data', f'{wuserid.value}bookmasterfixed.csv')
  booksdb.to_csv(ufile,index = False)

  # Combine books & booksdb - mylibrary
  # Load User books
  ufile = join(dirname(__file__), '../data', f'{wuserid.value}bookmasterfixed.csv')
  booksdb = pd.read_csv(ufile)

  ufile = join(dirname(__file__), '../data', f'{wuserid.value}books.csv')
  books = pd.read_csv(ufile)
  
  books = books.drop(columns=['Title', 'ISBN', 'Author'])
  booksdb = booksdb.drop(columns=['Id','format'])
  lib = pd.concat([books, booksdb], axis=1,)
  
  # Group the formats
  # Paperback Unbound Spiral-bound Unknown Binding Mass Market Paperback 
  # Hardcover Board book Leather Bound Library Binding 
  # Kindle Edition Nook ebook 
  # Audiobook Audio CD Audio Cassette Audible Audio CD-ROM MP3 CD 
  lib.Format[lib['Format']=='Unbound'] = 'Paperback'
  lib.Format[lib['Format']=='Spiral-bound'] = 'Paperback'
  lib.Format[lib['Format']=='Unknown Binding'] = 'Paperback'
  lib.Format[lib['Format']=='Mass Market Paperback'] = 'Paperback'
  lib.Format[lib['Format']=='Trade Paperback'] = 'Paperback'
  lib.Format[lib['Format']=='Board book'] = 'Hardcover'
  lib.Format[lib['Format']=='Hardcover Slipcased'] = 'Hardcover'
  lib.Format[lib['Format']=='Leather Bound'] = 'Hardcover'
  lib.Format[lib['Format']=='Library Binding'] = 'Hardcover'
  lib.Format[lib['Format']=='Nook'] = 'ebook'
  lib.Format[lib['Format']=='Kindle Edition'] = 'ebook'
  lib.Format[lib['Format']=='Audiobook'] = 'Audio'
  lib.Format[lib['Format']=='Audio CD'] = 'Audio'
  lib.Format[lib['Format']=='Audio Cassette'] = 'Audio'
  lib.Format[lib['Format']=='Audible Audio'] = 'Audio'
  lib.Format[lib['Format']=='CD-ROM'] = 'Audio'
  lib.Format[lib['Format']=='MP3 CD'] = 'Audio'
  filtertypes = ['Paperback', 'Hardcover', 'ebook', 'Audio']
  lib.Format[~lib['Format'].isin(filtertypes)] = 'Paperback'

  # print(lib.Format.unique()) #'Hardcover' 'Paperback' 'Audio' 'ebook'

  print('Data fixing completed')  
  # Save user library
  ufile = join(dirname(__file__), '../data', f'{wuserid.value}UserLibrary.csv')
  lib.to_csv(ufile) #,index=False)
  print(f'File {ufile} saved')  
  return lib
  
#---- Start of Selection ----*  

def process_data(wuserid):
  print('Book data processing started')
  lib = pd.DataFrame()
  # Read user book list from previous step
  ufile = join(dirname(__file__), '../data', f'{wuserid.value}books.csv')
  print(wuserid.value, ufile)
  books = pd.read_csv(ufile)
  print('books', len(books))
  if books.empty == True:
    print(f'books {ufile} not read')
    success = False
    return (lib, success)
  bookdb=pd.DataFrame(columns=bookcolumns)

# check if File read correctly
  for i in range(len(books)):
    id = books.Id[i]
    booksoup = get_booksoup(id) 
    if len(booksoup) <1:
      print('Booksoup not read correctly')
    bookdb=bookdb.append(get_bookmaster(id, booksoup)) #, ignore_index=False)
    progress = int(i/(len(books))*100)
    if progress%10 == 0 and progress%10 > 1:
       print(f'Reading book master {progress:0.0f}% completed')
    time.sleep(1)
  
# Save book db without
  ufile = join(dirname(__file__), '../data', f'{wuserid.value}bookmasternotfixed.csv')
  bookdb.to_csv(ufile) #,index=False)

  ufile = join(dirname(__file__), '../data', f'{wuserid.value}bookmasternotfixed.csv')
  bookdb = pd.read_csv(ufile)
  lib = fix_data(bookdb, wuserid)
  
  success = True
  if lib.empty == True:
    print('Error occurred while fixing the data')
    success = False
  print('Book data processing completed')  
  return lib, success
