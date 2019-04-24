from flask import Flask, request, render_template, Markup, session, redirect, url_for
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

conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cursor = conn.cursor()
cursor.execute("""DROP TABLE IF EXISTS food""")
conn.commit()



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
    keys VARCHAR(300) NOT NULL
  )
  """)


with open('fooddb.csv', 'r') as f:
  next(f)
  cursor.copy_from(f, 'food', sep=',')
conn.commit()

cart = {}
time = {}


@app.route("/")
def splash():
  if 'uid' not in session:
    session['uid'] = uuid.uuid4()
  
  return render_template("splash.html")

@app.route("/lunch")
def lunch():
  time[session['uid']] = 0
  return redirect(url_for('main'))

@app.route("/dinner")
def dinner():
  time[session['uid']] = 1
  return redirect(url_for('main'))

@app.route("/index")
def main():
  if 'uid' not in session:
    session['uid'] = uuid.uuid4()
    time[session['uid']] = 0
    
  sum = 0.0
  retVal2 = ""
  if cart.get(session['uid']) != None:
    for product in cart.get(session["uid"]):
      cursor.execute("SELECT price, image FROM food WHERE name=(%s)", (product,))
      query = cursor.fetchone()
      pre2 = '''<div class = "cart-item"> <span class="cart-item-title">'''
      post_title2 = '''</span> <span class="cart-price">$'''
      post_price2 = '''</span> <button class="btn btn-danger fa fa-minus" type="button" onclick="javascript:window.location='/removeItem/favorites/'''
      post_window2 = ''''"></button></div>'''
      retVal2 = retVal2 + (pre2 + str(product) + post_title2 + "{:.2f}".format(query[0]) + post_price2 + str(product) + post_window2)
      sum += float(query[0])

  retVal3 = '''$''' + "{:.2f}".format(sum)
  if cart.get(session['uid']) == None:
    return render_template("index.html", resultList3 = Markup(retVal3))

  return render_template("index.html", resultList2 = Markup(retVal2), resultList3 = Markup(retVal3))

@app.route("/contact")
def getContact():
    return render_template("contact.html")

@app.route("/favorites")
def getFavorites():
  if 'uid' not in session:
    session['uid'] = uuid.uuid4()
    time[session['uid']] = 0
    
  sum = 0.0
  retVal2 = ""
  if cart.get(session['uid']) != None:
    for product in cart.get(session["uid"]):
      cursor.execute("SELECT price, image FROM food WHERE name=(%s)", (product,))
      query = cursor.fetchone()
      pre2 = '''<div class = "cart-item"> <span class="cart-item-title">'''
      post_title2 = '''</span> <span class="cart-price">$'''
      post_price2 = '''</span> <button class="btn btn-danger fa fa-minus" type="button" onclick="javascript:window.location='/removeItem/favorites/'''
      post_window2 = ''''"></button></div>'''
      retVal2 = retVal2 + (pre2 + str(product) + post_title2 + "{:.2f}".format(query[0]) + post_price2 + str(product) + post_window2)
      sum += float(query[0])

  if time[session['uid']] == 0:
    selector = "dinner"
  else:
    selector = "lunch"
    
  cursor.execute("SELECT name, price, image, time FROM food WHERE time!=(%s) ORDER BY count DESC LIMIT 5", (selector,))
  results = cursor.fetchall()
  retVal = ""
  pre = '''<tr class="shop-item">
      <td class="shop-item-image"><h5>'''
  post_image = '''</h5></td>
      <td class="shop-item-title"><h5>'''
  post_title = '''</h5></td>
      <td class="shop-item-price"><h5>$'''
  post1 = '''</h5></td><td class="button" onclick="javascript:window.location='/addItem/favorites/'''
  urlend = ''''">'''
  post2 = '''
        <button class="btn btn-primary shop-item-button fas fa-plus" onclick="updateCartTotal();"></button>
      </td>
    </tr>'''
  if len(results) == 0:
    return "No results found."
  for re in results:
    retVal = retVal + (pre + str(re[2]) + post_image + str(re[0]) + post_title + "{:.2f}".format(re[1]) + post1 + str(re[0]) + urlend +  '''''' + post2)
    
  retVal3 = '''$''' + "{:.2f}".format(sum)

  if cart.get(session['uid']) == None:
    return render_template("favorites.html", resultList = Markup(retVal))
  return render_template("favorites.html", resultList = Markup(retVal), resultList2 = Markup(retVal2), resultList3 = Markup(retVal3))
  #return render_template("favorites.html", resultList = Markup(retVal))

@app.route("/info")
def getInfo():
    return render_template("info.html")

'''
def gettimeofday():
    time = request.form['time']
    if time == 1:
        return 'lunch'
    else:
        return 'dinner' '''

@app.route("/search/item/<item>")
def getItem(item):
  if 'uid' not in session:
    session['uid'] = uuid.uuid4()
    time[session['uid']] = 0
    
  sum = 0.0
  retVal2 = ""
  if cart.get(session['uid']) != None:
    for product in cart.get(session["uid"]):
      cursor.execute("SELECT price, image FROM food WHERE name=(%s)", (product,))
      query = cursor.fetchone()
      pre2 = '''<div class = "cart-item"> <span class="cart-item-title">'''
      post_title2 = '''</span> <span class="cart-price">$'''
      post_price2 = '''</span> <button class="btn btn-danger fa fa-minus" type="button" onclick="javascript:window.location='/removeItem/item/'''
      post_window2 = ''''"></button></div>'''
      retVal2 = retVal2 + (pre2 + str(product) + post_title2 + "{:.2f}".format(query[0]) + post_price2 + str(product) + post_window2)
      sum += float(query[0])

  if time[session['uid']] == 0:
    selector = "dinner"
  else:
    selector = "lunch"

  cursor.execute("SELECT name, price, image, time, keys FROM food WHERE time!=(%s) ORDER BY name", (selector,))
  results = cursor.fetchall()
  retVal = ""
  pre = '''<tr class="shop-item">
      <td class="shop-item-image"><h5>'''
  post_image = '''</h5></td>
      <td class="shop-item-title"><h5>'''
  post_title = '''</h5></td>
      <td class="shop-item-price"><h5>$'''
  post1 = '''</h5></td><td class="button" onclick="javascript:window.location='/addItem/item/'''
  urlend = ''''">'''
  post2 = '''
        <button class="btn btn-primary shop-item-button fas fa-plus"></button>
      </td>
    </tr>'''
  #<input type="submit" name="time_button">
  if len(results) == 0:
    return "No results found."
  for re in results:
      if (item.lower() in str(re[0]).lower()) or (item.lower() in str(re[4]).lower()):
        retVal = retVal + (pre + str(re[2]) + post_image + str(re[0]) + post_title + "{0:.2f}".format(re[1]) + post1 + str(re[0]) + urlend + post2)

  retVal3 = '''$''' + "{:.2f}".format(sum)

  if cart.get(session['uid']) == None:
    return render_template("results.html", resultList = Markup(retVal))
  return render_template("results.html", resultList = Markup(retVal), resultList2 = Markup(retVal2), resultList3 = Markup(retVal3))
  # return render_template("results.html", resultList = Markup(retVal)), resultList2 = Markup(retVal2))


@app.route("/search/category/<catg>")
def getItemsFromCategory(catg):
  if 'uid' not in session:
    session['uid'] = uuid.uuid4()
    time[session['uid']] = 0
    
  sum = 0.0
  retVal2 = ""
  if cart.get(session['uid']) != None:
    for product in cart.get(session["uid"]):
      cursor.execute("SELECT price, image FROM food WHERE name=(%s)", (product,))
      query = cursor.fetchone()
      pre2 = '''<div class = "cart-item"> <span class="cart-item-title">'''
      post_title2 = '''</span> <span class="cart-price">$'''
      post_price2 = '''</span> <button class="btn btn-danger fa fa-minus" type="button" onclick="javascript:window.location='/removeItem/'''
      #post_price2 = '''</span> <button class="btn btn-danger fa fa-minus" type="button" onclick="updateCartTotal(); removeItem(\''''
      post_window2 = ''''"></button></div>'''
      #post_window2 = '''\');"></button></div>'''
      retVal2 = retVal2 + (pre2 + str(product) + post_title2 + "{:.2f}".format(query[0]) + post_price2 + str(catg) + '''/''' + str(product) + post_window2)
      sum += float(query[0])
  
  if time[session['uid']] == 0:
    selector = "dinner"
  else:
    selector = "lunch"
    
  catg = str(catg)
  cursor.execute("SELECT name, price, image FROM food WHERE category=(%s) AND time!=(%s) ORDER BY name", (catg, selector,))
  results = cursor.fetchall()
  print(results)
  retVal = ""
  pre = '''<tr class="shop-item">
      <td class="shop-item-image"><h5>'''
  post_image = '''</h5></td>
      <td class="shop-item-title"><h5>'''
  post_title = '''</h5></td>
      <td class="shop-item-price"><h5>$'''
  post1 = '''</h5></td><td class="button" onclick="javascript:window.location='/addItem/'''
  #post1 = '''</h5></td><td class="button" onclick="updateCartTotal(); addItem(\''''
  urlend = ''''">'''
  #urlend = '''\');">'''
  post2 = '''
        <button class="btn btn-primary shop-item-button fas fa-plus" onclick="updateCartTotal();"></button>
      </td>
    </tr>'''
  if len(results) == 0:
    return "No results found."
  for re in results:
    retVal = retVal + (pre + str(re[2]) + post_image + str(re[0]) + post_title + "{:.2f}".format(re[1]) + post1 + str(catg) + '''/''' + str(re[0]) + urlend +  '''''' + post2)

  retVal3 = '''$''' + "{:.2f}".format(sum)
  if cart.get(session['uid']) == None:
    return render_template("category.html", resultList = Markup(retVal))

  return render_template("category.html", resultList = Markup(retVal), resultList2 = Markup(retVal2), resultList3 = Markup(retVal3))

@app.route("/checkout")
def checkout():
  session.pop('uid', None)
  return "You have checked out. Please let us know of any feedback you have!"


@app.route("/getsession")
def getsession():
  if 'uid' in session:
    return str(session['uid'])

  return "This messed up"


@app.route("/addItem/item/<search>/<item>")
def addItem(search, item):
  if cart.get(session['uid']) == None:
    cart[session['uid']] = []

  cart[session['uid']].append(item)
  cursor.execute("UPDATE food SET count=count+1 WHERE name=(%s)", (item,))

  string = "Your cart contains: "

  for purchase in cart[session['uid']]:
    string += str(purchase) + ", "
    
  cursor.execute("SELECT packaged FROM food WHERE name=(%s)", (item,))
  results = cursor.fetchall()
  print(results)

  return redirect(url_for('getItem', item=search))

@app.route("/addItem/<category>/<item>")
def addItemFromCategory(category, item):
  if cart.get(session['uid']) == None:
    cart[session['uid']] = []

  cart[session['uid']].append(item)
  cursor.execute("UPDATE food SET count=count+1 WHERE name=(%s)", (item,))

  string = "Your cart contains: "

  for purchase in cart[session['uid']]:
    string += str(purchase) + ", "

  return redirect(url_for('getItemsFromCategory', catg=category))

@app.route("/addItem/favorites/<item>")
def addItemFromFavorites(item):
  if cart.get(session['uid']) == None:
    cart[session['uid']] = []

  cart[session['uid']].append(item)
  cursor.execute("UPDATE food SET count=count+1 WHERE name=(%s)", (item,))

  string = "Your cart contains: "

  for purchase in cart[session['uid']]:
    string += str(purchase) + ", "

  return redirect(url_for('getFavorites'))

@app.route("/removeItem/item/<search>/<item>")
def removeItem(search, item):
  cart[session['uid']].remove(item)
  return redirect(url_for('getItem', item=search))

@app.route("/removeItem/<category>/<item>")
def removeItemFromCategory(category, item):
  cart[session['uid']].remove(item)
  return redirect(url_for('getItemsFromCategory', catg=category))

@app.route("/removeItemMain/<item>")
def removeItemFromMain(item):
  cart[session['uid']].remove(item)
  return redirect(url_for('main'))

@app.route("/removeItem/favorites/<item>")
def removeItemFromFavorites(item):
  cart[session['uid']].remove(item)
  return redirect(url_for('getFavorites'))

if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 5000))
    app.run(debug=False, port=PORT, host='0.0.0.0')
