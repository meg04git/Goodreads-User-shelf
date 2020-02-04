# Goodreads-User-shelf

This app gets Goodreads 'read' shelf id from user and display the users reading patterns.

After you clone, follow below steps: 
1. pip install -r requirements.txt
2. Run below command
      bokeh serve --show main.py

Note: Enter 'read' shelf id (On the Goodreads page, click on mybooks->readshelf, id will be between "/" and "?"). The app will be scraping Goodreads with limition - 1 request per second, for the first time/user. So it may take a while. However once user is in buffer, the output will be much quicker
