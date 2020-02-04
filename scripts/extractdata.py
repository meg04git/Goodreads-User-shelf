import datetime
import pandas as pd
import statistics
import requests
from bs4 import BeautifulSoup
import warnings
warnings.filterwarnings("ignore")

# os methods for manipulating paths
from os.path import dirname, join

from scripts.processdata import process_data

columns = (['Id','Title','ISBN','Author','Rating','AddDate','ReadDate','ReadYear','ReadWeekday','Format'])

def convert_date(iread_date):
  # Sat Dec 10 10:20:54 -0800 2016	
  #del (read_date, oread_date, read_year, read_weekday)
  read_date = iread_date[:20] + iread_date[26:31]
  read_date = datetime.datetime.strptime(read_date, "%c")
  oread_date = read_date.strftime("%x") 
  read_year = read_date.strftime("%Y")
  read_weekday = read_date.strftime("%a")
  return (oread_date, read_year, read_weekday)

def get_books(reviews):
  books=pd.DataFrame(columns=columns)
  for i,review in enumerate(reviews):
    books.loc[i,:]=''  #megha 1 feb
    books.at[i,'Id'] = review.find_all('id', {'type':'integer'})[0].get_text(strip = True)
    books.at[i,'Title'] = review.find_all(name = 'title')[0].get_text(strip = True)
    books.at[i,'ISBN'] = review.find_all(name = 'isbn')[0].get_text(strip = True)
    author = review.find_all(name = 'name')[0].get_text(strip = True)
    books.at[i,'Author'] = author 
    books.at[i,'Rating'] = review.find_all(name = 'rating')[0].get_text(strip = True)
    read_date = review.find_all(name = 'read_at')[0].get_text(strip = True)
    add_date = review.find_all(name = 'date_added')[0].get_text(strip = True)
    update_date = review.find_all(name = 'date_updated')[0].get_text(strip = True)
    if read_date == '':
      if update_date != '':
        read_date = update_date
      else:
        read_date = add_date
    read_date, read_year, read_weekday = convert_date(read_date)
    add_date, _, _ = convert_date(add_date)
    books.at[i,'AddDate'] = add_date
    books.at[i,'ReadDate'] = read_date
    books.at[i,'ReadYear'] = read_year
    books.at[i,'ReadWeekday'] = read_weekday
    books.at[i,'Format'] = review.find_all(name = 'format')[0].get_text(strip = True)
#    books.head()
    del (read_date, read_year, read_weekday, add_date, update_date, author)
  return books

def get_gr_data(userid, i, shelf):
  parameters = {
                'id': userid, # '7145096-megha', #Goodreads id of the user
                'shelf': shelf, #, currently-reading, to-read, etc. (optional)
                'sort': 'rating', #title, author, cover, rating, year_pub, date_pub, date_pub_edition, date_started, date_read, date_updated, date_added, recommender, avg_rating, num_ratings, review, read_count, votes, random, comments, notes, isbn, isbn13, asin, num_pages, format, position, shelves, owned, date_purchased, purchase_location, condition (optional)
                #  search[query]: query text to match against member's books (optional)
                # order: a, d (optional)
                'page': i, #'1-N', #(optional)
                'per_page': '200',# (optional)
                'key': 'hBFAWIoikCpkWn2JEjXyQ'   #Developer key (required).
                }
  soup = BeautifulSoup()
  success = True
  try:
    url = 'https://www.goodreads.com/review/list?v=2'

    response = requests.get(url, params=parameters)
    if response.status_code == 200:
      soup = BeautifulSoup(response.content, 'lxml') 
    else:
      success = False
  except:
    success = False
  if (success == False):
    print('Error occurred in extracting from GoodReads. Error code: ', response.status_code)
  return soup, success

def handle_submit_details(wuserid):

  userid=''
  userid= wuserid.value
  lib = pd.DataFrame()
  # #------------ Collect book reviews/books ------------#
  books=pd.DataFrame(columns=columns)
#  lprog.value = 10
  shelf='read'

  for i in range(10): #, start = 1):
    soup, success = get_gr_data(userid, i+1,shelf)
    if success == False:
      wuserid.value = 'Please enter valid Goodreads ID'
      return lib, success
    print(f'Extraction of books for {userid} from Goodreads started..')
    reviews = soup.find_all(name = 'review')
    books=books.append(get_books(reviews)) #, ignore_index=False)
    print(f'Extracting batch# {i+1}...')
    if len(reviews) < 200:
      break
  
  if success == False:
    return
  if books.empty:
    print('No data found')
    raise ValueError('No data found')
  print(f'Extraction complete...')
#  lprog.value = 90


  print(f'Data processing started...')

  #------------ Cleanup the data ------------#
  # dupbooks = (books[books.duplicated(['Title'],keep='last')])
  
  #Remove duplicates
  books.drop_duplicates(subset = 'Title', inplace=True)
  if books.empty:
    print('No data found')
    raise ValueError('No data found')
  # No missing values except for Format
  # Update format with most frequent using mode
  # Ratings could be missing for some users but we cannot randomly update it for now
  try:
    freqformat = statistics.mode(books['Format'])
  except:
    freqformat = mode(books['Format'])
  books.Format.at[books['Format']==''] = freqformat

#  lprog.value = 95

  #------------ Convert to Category datatype ------------#
  for col in ['Rating','ReadWeekday','Format']:
      books[col] = books[col].astype('category')

#  lprog.value = 98
  #------------ Save the user data for further processing / future use ------------#
  ufile = join(dirname(__file__), '../data', f'{userid}books.csv')
  books.to_csv(ufile, index = False)
  
  print(f'Data processing complete.')
#  lprog.value = 100

  lib, success = process_data(wuserid)
  return lib, success

def handle_submit(attr, old, new):
   return wuserid.value
  