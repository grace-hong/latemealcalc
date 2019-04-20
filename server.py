from flask import Flask, request, render_template, Markup, session
import os
import psycopg2
from psycopg2.extensions import AsIs
import subprocess
import os
import csv
import uuid


app = Flask(__name__, static_url_path = "", static_folder = "static")
app.secret_key = os.urandom(24)

#'heroku config:get DATABASE_URL -a calculatemeal' to get the name of the database
DATABASE_URL = 'postgres://gniojkvxziujuu:1c53b1d388891669097c66f2e618d42e31ffffa249aaaef45ccf72034503106c@ec2-184-73-153-64.compute-1.amazonaws.com:5432/d1ipk1vqr3fslq'

#READING CSV FILE FOR DATA #####################################################

conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cursor = conn.cursor()

##ADDED CODE ###################################################################################
cursor.execute("""DROP TABLE IF EXISTS food""")
conn.commit()
#################################################################################################


cursor.execute(
  """
  CREATE TABLE food (
    name VARCHAR(50) NOT NULL PRIMARY KEY,
    price REAL NOT NULL,
    category VARCHAR(50) NOT NULL,
    count INTEGER NOT NULL,
    time VARCHAR(50) NOT NULL,
    packaged VARCHAR(50) NOT NULL,
    image VARCHAR(50) NOT NULL,
    keys VARCHAR(50) NOT NULL
  )
  """)



with open('fooddb.csv', 'r') as f:
  next(f)
  cursor.copy_from(f, 'food', sep=',')
conn.commit()

cart = {}

#cursor.execute(
 #   """
  #  \copy food(name, price, category, count, time, packaged)
   # FROM 'fooddb.csv' DELIMITER ',' CSV HEADER
    #""")

@app.route("/")
def main():
  if 'uid' not in session:
    session['uid'] = uuid.uuid4()

  return render_template("index.html")

@app.route("/contact")
def getContact():
    return render_template("contact.html")

@app.route("/favorites")
def getFavorites():
  cursor.execute("SELECT name, price, image FROM food ORDER BY count DESC LIMIT 5")
  results = cursor.fetchall()
  retVal = ""
  pre = '''<tr class="shop-item">
      <td class="shop-item-image"><h5>'''
  post_image = '''</h5></td>
      <td class="shop-item-title"><h5>'''
  post_title = '''</h5></td>
      <td class="shop-item-price"><h5>$'''
  post = '''</h5></td><td class="button">
        <button class="btn btn-primary shop-item-button fas fa-plus"></button>
      </td>
    </tr>'''
  if len(results) == 0:
    return "No results found."
  for re in results:
    retVal = retVal + (pre + str(re[2]) + post_image + str(re[0]) + post_title + "{0:.2f}".format(re[1]) + post)

  return render_template("favorites.html", resultList = Markup(retVal))

@app.route("/info")
def getInfo():
    return render_template("info.html")

@app.route("/search/item/<item>")
def getItem(item):
  cursor.execute("SELECT name, price, image, time, keys FROM food")
  results = cursor.fetchall()
  retVal = ""
  pre = '''<tr class="shop-item">
      <td class="shop-item-image"><h5>'''
  post_image = '''</h5></td>
      <td class="shop-item-title"><h5>'''
  post_title = '''</h5></td>
      <td class="shop-item-price"><h5>$'''
  post = '''</h5></td><td class="button">
        <button class="btn btn-primary shop-item-button fas fa-plus"></button>
      </td>
    </tr>'''
  if len(results) == 0:
    return "No results found."
  for re in results:
      if (item.lower() in str(re[0]).lower()) or (item.lower() in str(re[4]).lower()):
        #if request.POST.get('lunchcheck', True): #print lunch item
        #if request.form.get('lunchcheck'):
          #if re[3].lower() == "lunch":
            #retVal = retVal + (pre + str(re[2]) + post_image + str(re[0]) + post_title + "{0:.2f}".format(re[1]) + post)
            #print(re[0])
        #elif request.POST.get('dinnercheck', True): #print dinner item
        #elif request.form.get('dinnercheck'):
          #if re[3].lower() == "both":
            #retVal = retVal + (pre + str(re[2]) + post_image + str(re[0]) + post_title + "{0:.2f}".format(re[1]) + post)
            #print(re[0])
        #else: #print item regardless of time
        retVal = retVal + (pre + str(re[2]) + post_image + str(re[0]) + post_title + "{0:.2f}".format(re[1]) + post)
        print(re[0])
        cursor.execute("UPDATE food SET count=count+1 WHERE name=(%s)", (re[0],))

  return render_template("results.html", resultList = Markup(retVal))


@app.route("/search/category/<catg>")
def getItemsFromCategory(catg):
  catg = str(catg)
  cursor.execute("SELECT name, price, image FROM food WHERE category=(%s)", (catg,))
  results = cursor.fetchall()
  print(results)
  retVal = ""
  pre = '''<tr class="shop-item">
      <td class="shop-item-image"><h5>'''
  post_image = '''</h5></td>
      <td class="shop-item-title"><h5>'''
  post_title = '''</h5></td>
      <td class="shop-item-price"><h5>$'''
  post1 = '''</h5></td><td class="button" '''
  urlpost = '''onclick="javascript:window.location='/addItem/''' + str(re[0]) + ''''">'''
  post2 = '''
        <button class="btn btn-primary shop-item-button fas fa-plus"></button>
      </td>
    </tr>'''
  if len(results) == 0:
    return "No results found."
  for re in results:
    retVal = retVal + (pre + str(re[2]) + post_image + str(re[0]) + post_title + "{0:.2f}".format(re[1]) + post1 + urlpost + str(re[0]) + '''''' + post2)

  return render_template("category.html", resultList = Markup(retVal))

@app.route("/checkout")
def checkout():
  session.pop('uid', None)
  return "You have checked out. Please let us know of any feedback you have!"


@app.route("/getsession")
def getsession():
  if 'uid' in session:
    return str(session['uid'])
  
  return "This messed up"


@app.route("/addItem/<item>")
def addItem(item):
  if 'cart' not in request.session:
    request.session['cart'] = {str(item)}
  else:
    request.session['cart'].update(str(item))
  return str(item)

if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 5000))
    app.run(debug=False, port=PORT, host='0.0.0.0')
