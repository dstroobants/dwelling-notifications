import time
import requests
import re
import mysql.connector
import os
from mailjet_rest import Client

# Wait for DB to be up (Need to fix that) 
time.sleep(20)

# Mysql Config
db = mysql.connector.connect(
  user="root",
  password="root",
  host="db",
  port="3306",
  database="dwellings"
)
cursor = db.cursor()

# Mailjet config
mailjet = Client(auth=(os.environ['MAILJET_API_KEY'], os.environ['MAILJET_API_SECRET']), version='v3.1')

first_run = True

def dwelling_exists(dwelling_id):
  sql = "SELECT * FROM links WHERE daft_id = %s"
  values = (dwelling_id, )
  cursor.execute(sql, values)
  result = cursor.fetchall()
  if result:
    for x in result:
      print('Dwelling found in DB: ', x)
    return(True)
  return False

def add_new_dwelling(dwelling_id, title, url):
  if 'daft.ie' in url:
    sql = "INSERT INTO links (daft_id, title, url) VALUES (%s, %s, %s)"
  elif 'myhome.ie' in url:
    sql = "INSERT INTO links (myhome_id, title, url) VALUES (%s, %s, %s)"
  values = (dwelling_id, title, url)
  cursor.execute(sql, values)
  db.commit()
  print('Dwelling added to DB: ', values)

def notify(dwelling_id, title, url):
  data = {
    'Messages': [
      {
        'From': {
          'Email': os.environ['EMAIL'],
          'Name': os.environ['NAME']
        },
        'To': [
          {
            'Email': os.environ['EMAIL'],
            'Name': os.environ['NAME']
          }
        ],
        'Subject': 'New dwelling - ' + dwelling_id,
        'HTMLPart': '<h3>New dwelling for rent</h3>' +
                    '<p>Title: ' + title + '</p>' +
                    '<p>Link: <a href=' + url + '>' + url + '</a></p>',
        'CustomID': dwelling_id
      }
    ]
  }
  mailjet.send.create(data=data)
  print('Notification Email Sent.')

while True:
  # Links for each daft dwellings are formatted like this:
  # "seoFriendlyPath":"/for-rent/from-here-student-living-cork-street-cork-street-dublin-8/2292148"
  #
  # Links for each MyHome dwellings are formatted like this:
  # <a class="PropertyListingCard__Address ng-tns-c206-49" 
  #   href="/rentals/brochure/fortal-villafortlawns-scalpwilliam-dalkey-co-dublin/4594117"> 
  #     Fortal VillaFortlawns, Scalpwilliam, Dalkey, Co. Dublin
  # </a>
  for search_url in os.environ['SEARCH_URLS'].split(','):
    try:
      r = requests.get(search_url) 
      if 'daft.ie' in search_url:
        dwellings = re.findall(r"(?<=seoFriendlyPath\":\")[^\"]*", r.text)
      elif 'myhome.ie' in search_url:
        dwellings = re.findall(r"(?<=class=\"PropertyListingCard__Address ..............\" href=\")[^\"]*", r.text)
    except:
      dwellings = ''
      print('\nCould not connect to: ', search_url)

    for elem in dwellings:
      print('\nElem:', elem)
      if 'daft.ie' in search_url:
        url = 'https://daft.ie' + elem
        elem = elem.split('/')
        title = elem[2]
        dwelling_id = int(elem[3])
      elif 'myhome.ie' in search_url:
        url = 'https://www.myhome.ie' + elem
        elem = elem.split('/')
        title = elem[3]
        dwelling_id = int(elem[4])
      print('\nDwelling ID:', dwelling_id)
      print('Title:', title)
      print('URL:', url)

      if not dwelling_exists(dwelling_id):
        add_new_dwelling(dwelling_id, title, url)
        if first_run == False:
          notify(dwelling_id, title, url)

  if first_run == True:
    first_run = False
    print('\nFirst Run, no notification email sent.')

  print('\nNext Search in 1 min.')
  time.sleep(60)
