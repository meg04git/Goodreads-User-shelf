# Goodreads-User-shelf

This app gets Goodreads 'read' shelf id from user and display the users reading patterns.

How to run:
1. Download repository
2. If you dont have Bokeh installed on your machine, the install using below commands:
      conda install bokeh 
              OR 
      pip install bokeh
3. In terminal/command prompt, Go to root folder where main.py file resides
4. Run below command
      bokeh serve --show main.py
5. A web page will open. Enter 'read' shelf id (On the Goodreads page, click on mybooks->readshelf, id will be between "/" and "?"). The app will be scraping Goodreads with limition - 1 request per second, for the first time/user. So it may take a while. However once user is in buffer, the output will be much quicker
