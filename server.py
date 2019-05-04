from flask import Flask, request, render_template, Markup, session, redirect, url_for, flash
import os
import psycopg2
from psycopg2.extensions import AsIs
import subprocess
import os
import csv
import uuid
import speech_recognition as sr

app = Flask(__name__, static_url_path = "", static_folder = "static")
app.secret_key = os.urandom(24)

#'heroku config:get DATABASE_URL -a calculatemeal' to get the name of the database
DATABASE_URL = 'postgres://gniojkvxziujuu:1c53b1d388891669097c66f2e618d42e31ffffa249aaaef45ccf72034503106c@ec2-184-73-153-64.compute-1.amazonaws.com:5432/d1ipk1vqr3fslq'

conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cursor = conn.cursor()
conn.commit()

'''
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
'''

recognizer = sr.Recognizer()

cart = {}
time = {}
packaged = {}
combos = {}
combosFull = {}
needAlert = {}

combosMain = ["Neapolitan Cheese Pizza", "Burrito", "Burrito Bowl", "Carved Entree with 2 sides", "Chicken and Waffles"]
combosAdd = ["Soda 16oz", "Milk Half Pint", "Apple", "Banana", "Grapefruit", "Nectarine", "Orange", "Peach", "Pear", "Plum", "Cookie (unwrapped)", "Small Grabngo Salad", "Juice 16oz"]

@app.route("/")
def splash():
  if 'uid' not in session:
    session['uid'] = uuid.uuid4()
    packaged[session['uid']] = 0
    combos[session['uid']] = 0
    combosFull[session['uid']] = 0

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
    packaged[session['uid']] = 0
    needAlert[session['uid']] = 0
    print("starting count")
    print(packaged[session['uid']])
    #print(packaged.get(session['uid]))

  sum = 0.0
  retVal2 = ""
  if cart.get(session['uid']) != None:
    for product in cart.get(session["uid"]):
      print(product)
      cursor.execute("SELECT price, image FROM food WHERE name=(%s)", (product,))
      query = cursor.fetchone()
      pre2 = '''<div class = "cart-block"><div class = "cart-item"> <span class="cart-item-title">'''
      post_title2 = '''</span> <span class="cart-price">$'''
      post_price2 = '''</span> <button class="btn btn-danger fa fa-minus" type="button" onclick="javascript:window.location='/removeItemMain/'''
      post_window2 = ''''"></button></div></div><br>'''
      retVal2 = retVal2 + (pre2 + str(product) + post_title2 + "{:.2f}".format(query[0]) + post_price2 + str(product) + post_window2)
      sum += float(query[0])

  if time[session['uid']] == 0:
    selector = "dinner"
  else:
    selector = "lunch"
  budget = 0.0
  if (selector == "dinner"):
    budget = 6.0
  else :
    budget = 7.0
  diff = budget - sum

  retVal3 = '''$''' + "{:.2f}".format(sum)

  retVal4 = ""
  cursor.execute("SELECT name, price, time, category FROM food WHERE time!=(%s) AND price <= (%s) AND category != (%s) ORDER BY count DESC LIMIT 10", (selector, diff, "unicorn", ))
  results2 = cursor.fetchall()
  for re in results2:
    if (str(re[0]) not in str(retVal2)):
      pre4 = '''<div class = "cart-block"><div class = "cart-item"> <span class="cart-item-title">'''
      post_title4 = '''</span> <span class="cart-price">$'''
      post_price4 = '''</span> <button class="btn btn-primary fa fa-plus" type="button" style="font-size: 10px; border-radius:3rem;" onclick="javascript:window.location='/addItem/'''
      post_window4 = ''''"></button></div></div><br>'''
      retVal4 = retVal4 + (pre4 + str(re[0]) + post_title4 + "{:.2f}".format(re[1]) + post_price4 + str(re[0]) + post_window4)

  if cart.get(session['uid']) == None:
    return render_template("index.html")
  if packaged.get(session['uid']) == 2 and needAlert.get(session['uid']) == 1 and diff >= 0:
    print('in this function')
    #retVal6 = ''' <script>confirm("You have reached the 2 packaged goods limit. Want to continue?") </script>'''
    retVal6 = ''' <script> if (alert("2 packaged goods only! Please try another item.")) {
			}
		</script> '''
    needAlert[session['uid']] = 0
    return render_template("index.html", resultList2 = Markup(retVal2), resultList3 = Markup(retVal3), resultList4 = Markup(retVal4), surplus = "${:.2f}".format(diff), packagedconfirm = Markup(retVal6),)
  if packaged.get(session['uid']) == 2 and needAlert.get(session['uid']) == 1 and diff < 0:
    #retVal6 = ''' <script>confirm("You have reached the 2 packaged goods limit. Want to continue?") </script>'''
    retVal6 = ''' <script> if (alert("2 packaged goods only! Please try another item.")) {
			} </script> '''
    needAlert[session['uid']] = 0
    return render_template("index.html", resultList2 = Markup(retVal2), resultList3 = Markup(retVal3), resultList4 = Markup(retVal4), diffOver = "${:.2f}".format(diff*-1), packagedconfirm = Markup(retVal6),)
  if diff >= 0:
    return render_template("index.html", resultList2 = Markup(retVal2), resultList3 = Markup(retVal3), resultList4 = Markup(retVal4), surplus = "${:.2f}".format(diff),)
  else:
    return render_template("index.html", resultList2 = Markup(retVal2), resultList3 = Markup(retVal3), resultList4 = Markup(retVal4), diffOver = "${:.2f}".format(diff*-1))

@app.route("/specials")
def getSpecials():
  if 'uid' not in session:
    session['uid'] = uuid.uuid4()
    time[session['uid']] = 0

  comboRet = ''''''
  if combosFull.get(session['uid']) == 1:
    comboRet = '''
    <div id='modal_dialog' style='background-color: #000000;'>
    	<div class='title' style='font-weight: 500; font-style: italic; color: white'>
    	</div>
    	<input type='button' value='yes' id='btnYes' class='btn-primary' style='font-weight: 400' />
    	<input type='button' value='no' id='btnNo' class='btn-primary' style='font-weight: 400' />
    </div>
    <script>
    dialog('You have added items to your cart that would qualify for a Late Meal combo during Late Meal hours. Would you like to make this a combo?',
    	function() {
		window.location = '/combos/default/yes';
	},
	function() {
		window.location = '/index';
	}
    );</script>'''
    print("Registered entire combo")

  if combos.get(session['uid']) == 1 and combosFull.get(session['uid']) != 1:
    comboRet = '''<script>alert('You have added a combo entree to your cart. Please navigate to the combos section for more information.')</script>'''
    print("Registered combo item")

  combos[session['uid']] = 0
  combosFull[session['uid']] = 0

  if time.get(session['uid']) == 0:
    selector = "dinner"
  else:
    selector = "lunch"
  
  sum = 0.0
  retVal2 = ""
  if cart.get(session['uid']) != None:
    for product in cart.get(session["uid"]):
      print(product)
      cursor.execute("SELECT price, image FROM food WHERE name=(%s)", (product,))
      query = cursor.fetchone()
      pre2 = '''<div class = "cart-block"><div class = "cart-item"> <span class="cart-item-title">'''
      post_title2 = '''</span> <span class="cart-price">$'''
      post_price2 = '''</span> <button class="btn btn-danger fa fa-minus" type="button" onclick="javascript:window.location='/removeItem/item/'''
      post_window2 = ''''"></button></div></div><br>'''
      retVal2 = retVal2 + (pre2 + str(product) + post_title2 + "{:.2f}".format(query[0]) + post_price2 + "late" + str(selector) + "special/" + str(product) + post_window2)
      sum += float(query[0])

  comboStr = ''''''

  retVal3 = '''$''' + "{:.2f}".format(sum)

  retVal4 = ""
  budget = 0.0
  if (selector == "dinner"):
    budget = 6.0
    comboStr = "Late Dinner Special " + '''<button class="btn btn-primary shop-item-button fas fa-plus" id="addition" onclick="window.location='/addItem/latedinnerspecial"></button>'''

  else :
    budget = 7.0
    comboStr = "Late Lunch Special " + '''<button class="btn btn-primary shop-item-button fas fa-plus" id="addition" onclick="window.location='/addItem/latelunchspecial"></button>'''

  diff = budget - sum

  cursor.execute("SELECT name, price, time, category FROM food WHERE time!=(%s) AND price <= (%s) AND category != (%s) ORDER BY count DESC LIMIT 10", (selector, diff, "unicorn", ))
  results2 = cursor.fetchall()
  for re in results2:
    if (str(re[0]) not in str(retVal2)):
      pre4 = '''<div class = "cart-block"><div class = "cart-item"> <span class="cart-item-title">'''
      post_title4 = '''</span> <span class="cart-price">$'''
      post_price4 = '''</span> <button class="btn btn-primary fa fa-plus" type="button" style="font-size: 10px; border-radius:3rem;" onclick="javascript:window.location='/addItem/item/Late '''
      post_window4 = ''''"></button></div></div><br>'''
      retVal4 = retVal4 + (pre4 + str(re[0]) + post_title4 + "{:.2f}".format(re[1]) + post_price4 + str(selector) + " Special/" + str(re[0]) + post_window4)

  if cart.get(session['uid']) == None:
    return render_template("specials.html")
  if packaged.get(session['uid']) == 2 and needAlert.get(session['uid']) == 1 and diff >= 0:
    print('in this function')
    retVal6 = ''' <script> if (alert("2 packaged goods only! Please try another item.")) {
			} </script> '''
    needAlert[session['uid']] = 0
    return render_template("specials.html", comboBtn=Markup(comboStr), resultList2 = Markup(retVal2), resultList3 = Markup(retVal3), surplus = "${:.2f}".format(diff), packagedconfirm = Markup(retVal6), resultList5 = Markup(comboRet))
  if packaged.get(session['uid']) > 2 and needAlert.get(session['uid']) == 1 and diff < 0:
    retVal6 = ''' <script> if (alert("2 packaged goods only! Please try another item.")) {
			}
			 </script> '''
    needAlert[session['uid']] = 0
    return render_template("specials.html", comboBtn=Markup(comboStr), resultList2 = Markup(retVal2), resultList3 = Markup(retVal3), diffOver = "${:.2f}".format(diff*-1), packagedconfirm = Markup(retVal6), resultList5 = Markup(comboRet))
  if diff >= 0:
    return render_template("specials.html", comboBtn=Markup(comboStr), resultList2 = Markup(retVal2), resultList3 = Markup(retVal3), resultList4 = Markup(retVal4), surplus = "${:.2f}".format(diff), resultList5 = Markup(comboRet))
  else:
    return render_template("specials.html", comboBtn=Markup(comboStr), resultList2 = Markup(retVal2), resultList3 = Markup(retVal3), resultList4 = Markup(retVal4), diffOver = "${:.2f}".format(diff*-1), resultList5 = Markup(comboRet))



@app.route("/favorites")
def getFavorites():
  if 'uid' not in session:
    session['uid'] = uuid.uuid4()
    time[session['uid']] = 0

  comboRet = ''''''
  if combosFull.get(session['uid']) == 1:
    comboRet = '''<script>combo();</script>'''
    print("Registered entire combo")

  if combos.get(session['uid']) == 1 and combosFull.get(session['uid']) != 1:
    comboRet = '''<script>alert('You have added a combo entree to your cart. Please navigate to the combos section for more information.')</script>'''
    print("Registered combo item")

  combos[session['uid']] = 0
  combosFull[session['uid']] = 0

  sum = 0.0
  retVal2 = ""
  if cart.get(session['uid']) != None:
    for product in cart.get(session["uid"]):
      print(product)
      cursor.execute("SELECT price, image FROM food WHERE name=(%s)", (product,))
      query = cursor.fetchone()
      pre2 = '''<div class = "cart-block"><div class = "cart-item"> <span class="cart-item-title">'''
      post_title2 = '''</span> <span class="cart-price">$'''
      post_price2 = '''</span> <button class="btn btn-danger fa fa-minus" type="button" onclick="javascript:window.location='/removeItemFavorites/'''
      post_window2 = ''''"></button></div></div><br>'''
      retVal2 = retVal2 + (pre2 + str(product) + post_title2 + "{:.2f}".format(query[0]) + post_price2 + str(product) + post_window2)
      sum += float(query[0])

  if time[session['uid']] == 0:
    selector = "dinner"
  else:
    selector = "lunch"
  budget = 0.0
  if (selector == "dinner"):
    budget = 6.0
  else :
    budget = 7.0
  diff = budget - sum
  cursor.execute("SELECT name, price, image, time, category FROM food WHERE time!=(%s) AND category!=(%s) ORDER BY count DESC LIMIT 5", (selector, "unicorn", ))
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
        <button class="btn btn-primary shop-item-button fas fa-plus" onclick="checkpackaged();"></button>
      </td>
    </tr>'''
  for re in results:
    retVal = retVal + (pre + str(re[2]) + post_image + str(re[0]) + post_title + "{:.2f}".format(re[1]) + post1 + str(re[0]) + urlend +  '''''' + post2)

  retVal3 = '''$''' + "{:.2f}".format(sum)

  retVal4 = ""
  budget = 0.0
  if (selector == "dinner"):
    budget = 6.0
  else :
    budget = 7.0

  diff = budget - sum

  cursor.execute("SELECT name, price, time, category FROM food WHERE time!=(%s) AND price <= (%s) AND category != (%s) ORDER BY count DESC LIMIT 10", (selector, diff, "unicorn", ))
  results2 = cursor.fetchall()
  for re in results2:
    if (str(re[0]) not in str(retVal2)):
      pre4 = '''<div class = "cart-block"><div class = "cart-item"> <span class="cart-item-title">'''
      post_title4 = '''</span> <span class="cart-price">$'''
      post_price4 = '''</span> <button class="btn btn-primary fa fa-plus" type="button" style="font-size: 10px; border-radius:3rem;" onclick="javascript:window.location='/addItem/favorites/'''
      post_window4 = ''''"></button></div></div><br>'''
      retVal4 = retVal4 + (pre4 + str(re[0]) + post_title4 + "{:.2f}".format(re[1]) + post_price4 + str(re[0]) + post_window4)

  if cart.get(session['uid']) == None:
    return render_template("favorites.html", resultList = Markup(retVal))
  if packaged.get(session['uid']) == 2 and needAlert.get(session['uid']) == 1 and diff >= 0:
    print('in this function')
    #retVal6 = ''' <script>confirm("You have reached the 2 packaged goods limit. Want to continue?") </script>'''
    retVal6 = ''' <script> if (alert("2 packaged goods only! Please try another item.")) {
			}
			</script> '''
    needAlert[session['uid']] = 0
    return render_template("favorites.html", resultList = Markup(retVal), resultList2 = Markup(retVal2), resultList3 = Markup(retVal3), resultList4 = Markup(retVal4), surplus = "${:.2f}".format(diff), packagedconfirm = Markup(retVal6), resultString5 = Markup(comboRet))
  if packaged.get(session['uid']) == 2 and needAlert.get(session['uid']) == 1 and diff < 0:
    #retVal6 = ''' <script>confirm("You have reached the 2 packaged goods limit. Want to continue?") </script>'''
    retVal6 = ''' <script> if (alert("2 packaged goods only! Please try another item.")) {
                	}</script> '''
    needAlert[session['uid']] = 0
    return render_template("favorites.html", resultList = Markup(retVal), resultList2 = Markup(retVal2), resultList3 = Markup(retVal3), resultList4 = Markup(retVal4), diffOver = "${:.2f}".format(diff*-1), packagedconfirm = Markup(retVal6), resultList5 = Markup(comboRet))
  if diff >= 0:
    return render_template("favorites.html", resultList = Markup(retVal), resultList2 = Markup(retVal2), resultList3 = Markup(retVal3), resultList4 = Markup(retVal4), surplus = "${:.2f}".format(diff), resultList5 = Markup(comboRet))
  else:
    return render_template("favorites.html", resultList = Markup(retVal), resultList2 = Markup(retVal2), resultList3 = Markup(retVal3), resultList4 = Markup(retVal4), diffOver = "${:.2f}".format(diff*-1), resultList5 = Markup(comboRet))

@app.route("/team")
def getTeam():
    return render_template("team.html")

@app.route("/info")
def getInfo():
  if 'uid' not in session:
    session['uid'] = uuid.uuid4()
    time[session['uid']] = 0

  sum = 0.0
  retVal2 = ""
  if cart.get(session['uid']) != None:
    for product in cart.get(session["uid"]):
      cursor.execute("SELECT price, image FROM food WHERE name=(%s)", (product,))
      query = cursor.fetchone()
      pre2 = '''<div class = "cart-block"><div class = "cart-item"> <span class="cart-item-title">'''
      post_title2 = '''</span> <span class="cart-price">$'''
      post_price2 = '''</span> <button class="btn btn-danger fa fa-minus" type="button" onclick="javascript:window.location='/removeItemInfo/'''
      post_window2 = ''''"></button></div></div><br>'''
      retVal2 = retVal2 + (pre2 + str(product) + post_title2 + "{:.2f}".format(query[0]) + post_price2 + str(product) + post_window2)
      sum += float(query[0])

  if time[session['uid']] == 0:
    selector = "dinner"
  else:
    selector = "lunch"
  budget = 0.0
  if (selector == "dinner"):
    budget = 6.0
  else :
    budget = 7.0
  diff = budget - sum

  retVal3 = '''$''' + "{:.2f}".format(sum)

  retVal4 = ""
  cursor.execute("SELECT name, price, time, category FROM food WHERE time!=(%s) AND price <= (%s) AND category != (%s) ORDER BY count DESC LIMIT 10", (selector, diff, "unicorn", ))
  results2 = cursor.fetchall()
  for re in results2:
    if (str(re[0]) not in str(retVal2)):
      pre4 = '''<div class = "cart-block"><div class = "cart-item"> <span class="cart-item-title">'''
      post_title4 = '''</span> <span class="cart-price">$'''
      post_price4 = '''</span> <button class="btn btn-primary fa fa-plus" type="button" style="font-size: 10px; border-radius:3rem;" onclick="javascript:window.location='/addItem/info/'''
      post_window4 = ''''"></button></div></div><br>'''
      retVal4 = retVal4 + (pre4 + str(re[0]) + post_title4 + "{:.2f}".format(re[1]) + post_price4 + str(re[0]) + post_window4)

  if cart.get(session['uid']) == None:
    return render_template("info.html")
  if packaged.get(session['uid']) == 2 and needAlert.get(session['uid']) == 1 and diff >= 0:
    print('in this function')
    #retVal6 = ''' <script>confirm("You have reached the 2 packaged goods limit. Want to continue?") </script>'''
    retVal6 = ''' <script> if (alert("2 packaged goods only! Please try another item.")) {
			}
			 </script> '''
    needAlert[session['uid']] = 0
    return render_template("info.html", resultList2 = Markup(retVal2), resultList3 = Markup(retVal3), resultList4 = Markup(retVal4), surplus = "${:.2f}".format(diff), packagedconfirm = Markup(retVal6), resultString5 = Markup(comboRet))
  if packaged.get(session['uid']) == 2 and needAlert.get(session['uid']) == 1 and diff < 0:
    #retVal6 = ''' <script>confirm("You have reached the 2 packaged goods limit. Want to continue?") </script>'''
    retVal6 = ''' <script> if (alert("2 packaged goods only! Please try another item.")) {
			}
			 </script> '''
    needAlert[session['uid']] = 0
    return render_template("info.html", resultList2 = Markup(retVal2), resultList3 = Markup(retVal3), resultList4 = Markup(retVal4), diffOver = "${:.2f}".format(diff*-1), packagedconfirm = Markup(retVal6), resultList5 = Markup(comboRet))
  if diff >= 0:
    return render_template("info.html", resultList2 = Markup(retVal2), resultList3 = Markup(retVal3), resultList4 = Markup(retVal4), surplus = "${:.2f}".format(diff),)
  else:
    return render_template("info.html", resultList2 = Markup(retVal2), resultList3 = Markup(retVal3), resultList4 = Markup(retVal4), diffOver = "-${:.2f}".format(diff*-1),)

@app.route("/install")
def getInstall():
  if 'uid' not in session:
    session['uid'] = uuid.uuid4()
    time[session['uid']] = 0

  return render_template("install.html")


@app.route("/search/item/<item>")
def getItem(item):
  if 'uid' not in session:
    session['uid'] = uuid.uuid4()
    time[session['uid']] = 0

  if item == "title.png":
    return app.send_static_file('title.png')

  comboRet = ''''''
  if combosFull.get(session['uid']) == 1:
    comboRet = '''<script>combo();</script>'''
    print("Registered entire combo")

  if combos.get(session['uid']) == 1 and combosFull.get(session['uid']) != 1:
    comboRet = '''<script>alert('You have added a combo entree to your cart. Please navigate to the combos section for more information.')</script>'''
    print("Registered combo item")

  combos[session['uid']] = 0
  combosFull[session['uid']] = 0

  sum = 0.0
  retVal2 = ""
  if cart.get(session['uid']) != None:
    for product in cart.get(session["uid"]):
      print(product)
      cursor.execute("SELECT price, image FROM food WHERE name=(%s)", (product,))
      query = cursor.fetchone()
      pre2 = '''<div class = "cart-block"><div class = "cart-item"> <span class="cart-item-title">'''
      post_title2 = '''</span> <span class="cart-price">$'''
      post_price2 = '''</span> <button class="btn btn-danger fa fa-minus" type="button" onclick="javascript:window.location='/removeItem/item/'''
      post_window2 = ''''"></button></div></div><br>'''
      retVal2 = retVal2 + (pre2 + str(product) + post_title2 + "{:.2f}".format(query[0]) + post_price2 + str(item) + "/" + str(product) + post_window2)
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
  for re in results:
      if (item.lower() in str(re[0]).lower()) or (item.lower() in str(re[4]).lower()):
        retVal = retVal + (pre + str(re[2]) + post_image + str(re[0]) + post_title + "{0:.2f}".format(re[1]) + post1 + str(item) + "/"+ str(re[0]) + urlend + post2)

  retVal3 = '''$''' + "{:.2f}".format(sum)

  retVal4 = ""
  budget = 0.0
  if (selector == "dinner"):
    budget = 6.0
  else :
    budget = 7.0

  diff = budget - sum

  cursor.execute("SELECT name, price, time, category FROM food WHERE time!=(%s) AND price <= (%s) AND category != (%s) ORDER BY count DESC LIMIT 10", (selector, diff, "unicorn", ))
  results2 = cursor.fetchall()
  for re in results2:
    if (str(re[0]) not in str(retVal2)):
      pre4 = '''<div class = "cart-block"><div class = "cart-item"> <span class="cart-item-title">'''
      post_title4 = '''</span> <span class="cart-price">$'''
      post_price4 = '''</span> <button class="btn btn-primary fa fa-plus" type="button" style="font-size: 10px; border-radius:3rem;" onclick="javascript:window.location='/addItem/item/'''
      post_window4 = ''''"></button></div></div><br>'''
      retVal4 = retVal4 + (pre4 + str(re[0]) + post_title4 + "{:.2f}".format(re[1]) + post_price4 + str(item) + "/" + str(re[0]) + post_window4)

  if cart.get(session['uid']) == None:
    return render_template("results.html", resultList = Markup(retVal))
  if packaged.get(session['uid']) == 2 and needAlert.get(session['uid']) == 1 and diff >= 0:
    print('in this function')
    #retVal6 = ''' <script>confirm("You have reached the 2 packaged goods limit. Want to continue?") </script>'''
    retVal6 = ''' <script> if (alert("2 packaged goods only! Please try another item.")) {
			} </script> '''
    needAlert[session['uid']] = 0
    return render_template("results.html", resultList = Markup(retVal), resultList2 = Markup(retVal2), resultList3 = Markup(retVal3), surplus = "${:.2f}".format(diff), packagedconfirm = Markup(retVal6), resultList5 = Markup(comboRet))
  if packaged.get(session['uid']) == 2 and needAlert.get(session['uid']) == 1 and diff < 0:
    #retVal6 = ''' <script>confirm("You have reached the 2 packaged goods limit. Want to continue?") </script>'''
    retVal6 = ''' <script> if (alert("2 packaged goods only! Please try another item.")) {
			}
			 </script> '''
    needAlert[session['uid']] = 0
    return render_template("results.html", resultList = Markup(retVal), resultList2 = Markup(retVal2), resultList3 = Markup(retVal3), diffOver = "${:.2f}".format(diff*-1), packagedconfirm = Markup(retVal6), resultList5 = Markup(comboRet))
  if diff >= 0:
    return render_template("results.html", resultList = Markup(retVal), resultList2 = Markup(retVal2), resultList3 = Markup(retVal3), resultList4 = Markup(retVal4), surplus = "${:.2f}".format(diff), resultList5 = Markup(comboRet))
  else:
    return render_template("results.html", resultList = Markup(retVal), resultList2 = Markup(retVal2), resultList3 = Markup(retVal3), resultList4 = Markup(retVal4), diffOver = "${:.2f}".format(diff*-1), resultList5 = Markup(comboRet))

@app.route("/search/category/<catg>")
def getItemsFromCategory(catg):
  if 'uid' not in session:
    session['uid'] = uuid.uuid4()
    time[session['uid']] = 0

  if catg == "title.png":
    return app.send_static_file('title.png')

  comboRet = ''''''
  if combosFull.get(session['uid']) == 1:
    comboRet = '''<script>combo();</script>'''
    print("Registered entire combo")

  if combos.get(session['uid']) == 1 and combosFull.get(session['uid']) != 1:
    comboRet = '''<script>alert('You have added a combo entree to your cart. Please navigate to the combos section for more information.')</script>'''
    print("Registered combo item")

  combos[session['uid']] = 0
  combosFull[session['uid']] = 0

  sum = 0.0
  retVal2 = ""
  if cart.get(session['uid']) != None:
    for product in cart.get(session["uid"]):
      print(product)
      cursor.execute("SELECT price, image FROM food WHERE name=(%s)", (product,))
      query = cursor.fetchone()
      pre2 = '''<div class = "cart-block"><div class = "cart-item"> <span class="cart-item-title">'''
      post_title2 = '''</span> <span class="cart-price">$'''
      post_price2 = '''</span> <button class="btn btn-danger fa fa-minus" type="button" onclick="javascript:window.location='/removeItem/'''
      post_window2 = ''''"></button></div></div><br>'''
      retVal2 = retVal2 + (pre2 + str(product) + post_title2 + "{:.2f}".format(query[0]) + post_price2 + str(catg) + '''/''' + str(product) + post_window2)
      sum += float(query[0])

  if time[session['uid']] == 0:
    selector = "dinner"
  else:
    selector = "lunch"

  budget = 0.0
  if (selector == "dinner"):
    budget = 6.0
  else :
    budget = 7.0
  diff = budget - sum

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
  urlend = ''''">'''
  post2 = '''
        <button class="btn btn-primary shop-item-button fas fa-plus" id="addition" onclick="checkpackaged();"></button>
      </td>
    </tr>'''

  for re in results:
    retVal = retVal + (pre + str(re[2]) + post_image + str(re[0]) + post_title + "{:.2f}".format(re[1]) + post1 + str(catg) + '''/''' + str(re[0]) + urlend +  '''''' + post2)

  retVal3 = '''$''' + "{:.2f}".format(sum)
  retVal4 = ""
  budget = 0.0
  if (selector == "dinner"):
    budget = 6.0
  else :
    budget = 7.0

  diff = budget - sum

  cursor.execute("SELECT name, price, time, category FROM food WHERE time!=(%s) AND price <= (%s) AND category != (%s) ORDER BY count DESC LIMIT 10", (selector, diff, "unicorn", ))
  results2 = cursor.fetchall()
  for re in results2:
    if (str(re[0]) not in str(retVal2)):
      pre4 = '''<div class = "cart-block"><div class = "cart-item"> <span class="cart-item-title">'''
      post_title4 = '''</span> <span class="cart-price">$'''
      post_price4 = '''</span> <button class="btn btn-primary fa fa-plus" type="button" style="font-size: 10px; border-radius:3rem;" onclick="javascript:window.location='/addItem/'''
      post_window4 = ''''"></button></div></div><br>'''
      retVal4 = retVal4 + (pre4 + str(re[0]) + post_title4 + "{:.2f}".format(re[1]) + post_price4 + str(catg) + "/" + str(re[0]) + post_window4)

  if cart.get(session['uid']) == None:
    print(comboRet)
    return render_template("category.html", resultList = Markup(retVal))
  if packaged.get(session['uid']) == 2 and needAlert.get(session['uid']) == 1 and diff >= 0:
    print('in this function')
    #retVal6 = ''' <script>confirm("You have reached the 2 packaged goods limit. Want to continue?") </script>'''
    retVal6 = ''' <script> if (alert("2 packaged goods only! Please try another item.")) {
			}
			</script> '''
    needAlert[session['uid']] = 0
    return render_template("category.html", resultList = Markup(retVal), resultList2 = Markup(retVal2), resultList3 = Markup(retVal3), surplus = "${:.2f}".format(diff), packagedconfirm = Markup(retVal6), resultList5 = Markup(comboRet))
  if packaged.get(session['uid']) == 2 and needAlert.get(session['uid']) == 1 and diff < 0:
   #retVal6 = ''' <script>confirm("You have reached the 2 packaged goods limit. Want to continue?") </script>'''
    retVal6 = ''' <script> if (alert("2 packaged goods only! Please try another item.")) {
			}
			</script> '''
    needAlert[session['uid']] = 0
    return render_template("category.html", resultList = Markup(retVal), resultList2 = Markup(retVal2), resultList3 = Markup(retVal3), diffOver = "${:.2f}".format(diff*-1), packagedconfirm = Markup(retVal6), resultList5 = Markup(comboRet))
  if diff >= 0:
    print("This 2")
    print(comboRet)
    return render_template("category.html", resultList = Markup(retVal), resultList2 = Markup(retVal2), resultList3 = Markup(retVal3), resultList4 = Markup(retVal4), surplus = "${:.2f}".format(diff), resultList5 = Markup(comboRet))
  else:
    print("This 3")
    print(comboRet)
    return render_template("category.html", resultList = Markup(retVal), resultList2 = Markup(retVal2), resultList3 = Markup(retVal3), resultList4 = Markup(retVal4), diffOver = "${:.2f}".format(diff*-1), resultList5 = Markup(comboRet))

@app.route("/checkout")
def checkout():
  if cart.get(session['uid']) != None:
  	cart.pop(session['uid'])
  if time.get(session['uid']) != None:
  	time.pop(session['uid'])
  session.pop('uid', None)
  return redirect(url_for('splash'))


@app.route("/getsession")
def getsession():
  if 'uid' in session:
    return str(session['uid'])

  return "This messed up"


@app.route("/addItem/item/<search>/<item>")
def addItem(search, item):
  if cart.get(session['uid']) == None:
    cart[session['uid']] = []

  cursor.execute("SELECT packaged FROM food WHERE name=(%s)", (item,))
  results = cursor.fetchall()
  if str(results[0]) == ('(\'y\',)') and packaged.get(session['uid']) == 2:
    needAlert[session['uid']] = 1
    return redirect(url_for('getItem', item=search))
  elif str(results[0]) == ('(\'y\',)'):
    packaged[session['uid']] = packaged.get(session['uid']) + 1
    print('matched')
  print(results)
  print(packaged.get(session['uid']))

  # cart[session['uid']].append(item)
  print(item)
  cursor.execute("UPDATE food SET count=count+1 WHERE name=(%s)", (item,))
  conn.commit()
  pizza = 0
  boolean = 0
  booleanSides = 0
  for main in combosMain:
    if item == main:
      combos[session['uid']] = 1
      if item == "Neapolitan Cheese Pizza":
        boolean = 2
     
      else:
        boolean = 1
  
  for side in combosAdd:
    if item == side:
      booleanSides = 1
      if item == "Cookie (unwrapped)":
        booleanSides = 2
  
  cookies = 0
  for product in cart[session['uid']]:
    if product == "Cookie (unwrapped)":
      cookies += 1

  counterMain = 0
  counterAdd = 0
  for purchase in cart[session['uid']]:
    if purchase in combosMain:
      counterMain += 1
      if purchase == "Neapolitan Cheese Pizza":
        pizza += 1
    if purchase in combosAdd:
      counterAdd += 1


  if boolean != 0:
    if ((counterMain == 0 and boolean == 1) or (counterMain >= 1 and boolean == 2)) and ((counterAdd == 2 and cookies == 0) or (counterAdd == 3 and cookies >= 2) or (counterAdd == 4 and cookies >= 3)): 
      combosFull[session['uid']] = 1
    else:
      combosFull[session['uid']] = 0

  else:
    if ((counterMain == 1 and pizza != 1) or (counterMain == 2 and pizza >= 2)) and ((counterAdd == 1 and booleanSides == 1) or (counterAdd == 2 and ((cookies == 1 and booleanSides == 2) or (cookies == 2 and booleanSides == 1))) or (counterAdd == 3 and cookies == 3 and booleanSides == 2)):
      combosFull[session['uid']] = 1
    else:
      combosFull[session['uid']] = 0

  cart[session['uid']].append(item)
  return redirect(url_for('getItem', item=search))

@app.route("/addItem/<category>/<item>")
def addItemFromCategory(category, item):
  if cart.get(session['uid']) == None:
    cart[session['uid']] = []

  cursor.execute("SELECT packaged FROM food WHERE name=(%s)", (item,))
  results = cursor.fetchall()
  print(packaged.get(session['uid']))
  if str(results[0]) == ('(\'y\',)') and packaged.get(session['uid']) == 2:
    needAlert[session['uid']] = 1
    return redirect(url_for('getItemsFromCategory', catg=category))
  elif str(results[0]) == ('(\'y\',)'):
    packaged[session['uid']] = packaged.get(session['uid']) + 1
    print('matched')
  print(results)
  print(packaged.get(session['uid']))

  print(item)
  cursor.execute("UPDATE food SET count=count+1 WHERE name=(%s)", (item,))
  conn.commit()

  pizza = 0
  boolean = 0
  booleanSides = 0
  for main in combosMain:
    if item == main:
      combos[session['uid']] = 1
      if item == "Neapolitan Cheese Pizza":
        boolean = 2
     
      else:
        boolean = 1
  
  for side in combosAdd:
    if item == side:
      booleanSides = 1
      if item == "Cookie (unwrapped)":
        booleanSides = 2
  
  cookies = 0
  for product in cart[session['uid']]:
    if product == "Cookie (unwrapped)":
      cookies += 1

  counterMain = 0
  counterAdd = 0
  for purchase in cart[session['uid']]:
    if purchase in combosMain:
      counterMain += 1
      if purchase == "Neapolitan Cheese Pizza":
        pizza += 1
    if purchase in combosAdd:
      counterAdd += 1


  if boolean != 0:
    if ((counterMain == 0 and boolean == 1) or (counterMain >= 1 and boolean == 2)) and ((counterAdd == 2 and cookies == 0) or (counterAdd == 3 and cookies >= 2) or (counterAdd == 4 and cookies >= 3)): 
      combosFull[session['uid']] = 1
    else:
      combosFull[session['uid']] = 0

  else:
    if ((counterMain == 1 and pizza != 1) or (counterMain == 2 and pizza >= 2)) and ((counterAdd == 1 and booleanSides == 1) or (counterAdd == 2 and ((cookies == 1 and booleanSides == 2) or (cookies == 2 and booleanSides == 1))) or (counterAdd == 3 and cookies == 3 and booleanSides == 2)):
      combosFull[session['uid']] = 1
    else:
      combosFull[session['uid']] = 0

  cart[session['uid']].append(item)
  if item == 'Late Lunch Special' or item == 'Late Dinner Special':
      return redirect(url_for('main'))
  else:
      return redirect(url_for('getItemsFromCategory', catg=category))

@app.route("/addItem/favorites/<item>")
def addItemFromFavorites(item):
  if cart.get(session['uid']) == None:
    cart[session['uid']] = []
    time[session['uid']] = 0

  cursor.execute("SELECT packaged FROM food WHERE name=(%s)", (item,))
  results = cursor.fetchall()
  print(packaged.get(session['uid']))
  if packaged.get(session['uid']) > 2:
    print('in this function /addItem/favorites/<item>')
  if str(results[0]) == ('(\'y\',)') and packaged.get(session['uid']) == 2:
    needAlert[session['uid']] = 1
    return redirect(url_for('getFavorites'))
  elif str(results[0]) == ('(\'y\',)'):
    packaged[session['uid']] = packaged.get(session['uid']) + 1
    print('matched')
  print(results)
  print(packaged.get(session['uid']))

  # cart[session['uid']].append(item)
  print(item)
  cursor.execute("UPDATE food SET count=count+1 WHERE name=(%s)", (item,))
  conn.commit()
  
  pizza = 0
  boolean = 0
  booleanSides = 0
  for main in combosMain:
    if item == main:
      combos[session['uid']] = 1
      if item == "Neapolitan Cheese Pizza":
        boolean = 2
     
      else:
        boolean = 1
  
  for side in combosAdd:
    if item == side:
      booleanSides = 1
      if item == "Cookie (unwrapped)":
        booleanSides = 2
  
  cookies = 0
  for product in cart[session['uid']]:
    if product == "Cookie (unwrapped)":
      cookies += 1

  counterMain = 0
  counterAdd = 0
  for purchase in cart[session['uid']]:
    if purchase in combosMain:
      counterMain += 1
      if purchase == "Neapolitan Cheese Pizza":
        pizza += 1
    if purchase in combosAdd:
      counterAdd += 1


  if boolean != 0:
    if ((counterMain == 0 and boolean == 1) or (counterMain >= 1 and boolean == 2)) and ((counterAdd == 2 and cookies == 0) or (counterAdd == 3 and cookies >= 2) or (counterAdd == 4 and cookies >= 3)): 
      combosFull[session['uid']] = 1
    else:
      combosFull[session['uid']] = 0

  else:
    if ((counterMain == 1 and pizza != 1) or (counterMain == 2 and pizza >= 2)) and ((counterAdd == 1 and booleanSides == 1) or (counterAdd == 2 and ((cookies == 1 and booleanSides == 2) or (cookies == 2 and booleanSides == 1))) or (counterAdd == 3 and cookies == 3 and booleanSides == 2)):
      combosFull[session['uid']] = 1
    else:
      combosFull[session['uid']] = 0

  cart[session['uid']].append(item)
  return redirect(url_for('getFavorites'))

@app.route("/addItem/info/<item>")
def addItemFromInfo(item):
  if cart.get(session['uid']) == None:
    cart[session['uid']] = []

  cursor.execute("SELECT packaged FROM food WHERE name=(%s)", (item,))
  results = cursor.fetchall()
  print(packaged.get(session['uid']))
  if str(results[0]) == ('(\'y\',)') and packaged.get(session['uid']) == 2:
    needAlert[session['uid']] = 1
    return redirect(url_for('getInfo'))
  elif str(results[0]) == ('(\'y\',)'):
    packaged[session['uid']] = packaged[session['uid']] + 1
    print('matched')
  print(results)
  print(packaged.get(session['uid']))

  cart[session['uid']].append(item)
  print(item)
  cursor.execute("UPDATE food SET count=count+1 WHERE name=(%s)", (item,))
  conn.commit()

  string = "Your cart contains: "

  for purchase in cart[session['uid']]:
    string += str(purchase) + ", "
  return redirect(url_for('getInfo'))

@app.route("/addItem/<item>")
def addItemFromMain(item):
  if cart.get(session['uid']) == None:
    cart[session['uid']] = []
  cursor.execute("SELECT packaged FROM food WHERE name=(%s)", (item,))
  results = cursor.fetchall()
  print(str(results[0]))
  print('testing the session')
  print(packaged.get(session['uid']))
  if packaged.get(session['uid']) > 2:
    print('in this function /addItem/item/<search>/<item>')
  if str(results[0]) == ('(\'y\',)') and packaged.get(session['uid']) == 2:
    needAlert[session['uid']] = 1
    return redirect(url_for('main'))
  elif str(results[0]) == ('(\'y\',)'):
    packaged[session['uid']] = packaged.get(session['uid']) + 1
    print('matched')

  # cart[session['uid']].append(item)
  print(item)
  cursor.execute("UPDATE food SET count=count+1 WHERE name=(%s)", (item,))
  conn.commit()

  pizza = 0
  boolean = 0
  booleanSides = 0
  for main in combosMain:
    if item == main:
      combos[session['uid']] = 1
      if item == "Neapolitan Cheese Pizza":
        boolean = 2
     
      else:
        boolean = 1
  
  for side in combosAdd:
    if item == side:
      booleanSides = 1
      if item == "Cookie (unwrapped)":
        booleanSides = 2
  
  cookies = 0
  for product in cart[session['uid']]:
    if product == "Cookie (unwrapped)":
      cookies += 1

  counterMain = 0
  counterAdd = 0
  for purchase in cart[session['uid']]:
    if purchase in combosMain:
      counterMain += 1
      if purchase == "Neapolitan Cheese Pizza":
        pizza += 1
    if purchase in combosAdd:
      counterAdd += 1


  if boolean != 0:
    if ((counterMain == 0 and boolean == 1) or (counterMain >= 1 and boolean == 2)) and ((counterAdd == 2 and cookies == 0) or (counterAdd == 3 and cookies >= 2) or (counterAdd == 4 and cookies >= 3)): 
      combosFull[session['uid']] = 1
    else:
      combosFull[session['uid']] = 0

  else:
    if ((counterMain == 1 and pizza != 1) or (counterMain == 2 and pizza >= 2)) and ((counterAdd == 1 and booleanSides == 1) or (counterAdd == 2 and ((cookies == 1 and booleanSides == 2) or (cookies == 2 and booleanSides == 1))) or (counterAdd == 3 and cookies == 3 and booleanSides == 2)):
      combosFull[session['uid']] = 1
    else:
      combosFull[session['uid']] = 0
  
  cart[session['uid']].append(item)
  return redirect(url_for('main'))

@app.route("/combos/favorites/yes")
def combosFavYes():
  print("Printing cart:")
  print(cart[session['uid']])
  newCart = cart[session['uid']].copy()
  delAdd = 0
  delMain = 0
  for product in newCart:
    print("product"),
    print(product)
    if product in combosMain and delMain < 1:
      print("main"),
      print(product)
      cart[session['uid']].remove(product)
      delMain += 1

    if product in combosAdd and delAdd < 2:
      print("side"),
      print(product)
      cart[session['uid']].remove(product)
      delAdd += 1

  if time.get(session['uid']) == 1:
    cart[session['uid']].append("Late Dinner Special")

  else:
    cart[session['uid']].append("Late Lunch Special")
  packaged[session['uid']] = 0
  return redirect(url_for('getFavorites'))

# we need to change this to reload the old page lol
@app.route("/combos/default/yes")
def combosDefaultYes():
  print("Printing cart:")
  print(cart[session['uid']])
  newCart = cart[session['uid']].copy()
  delAdd = 0
  delMain = 0
  bound1 = 1
  bound2 = 2
  pizza = 0
  cookies = 0
  for product in newCart:
    if product == "Neapolitan Cheese Pizza":
      pizza += 1
    if product == "Cookie (unwrapped)":
      cookies += 1

  if pizza == 2:
    bound1 = 2
  if cookies == 2:
    bound2 = 3
  if cookies == 4:
    bound2 = 4

  for product in newCart:
    print("product"),
    print(product)
    if product in combosMain and delMain < bound1:
      print("main"),
      print(product)
      cart[session['uid']].remove(product)
      delMain += 1

    if product in combosAdd and delAdd < bound2:
      print("side"),
      print(product)
      cart[session['uid']].remove(product)
      delAdd += 1

  if time.get(session['uid']) == 1:
    cart[session['uid']].append("Late Dinner Special")

  else:
    cart[session['uid']].append("Late Lunch Special")
  packaged[session['uid']] = 0
  return redirect(url_for('main'))

@app.route("/removeItem/item/<search>/<item>")
def removeItem(search, item):
  cursor.execute("SELECT packaged FROM food WHERE name=(%s)", (item,))
  results = cursor.fetchall()
  print(packaged.get(session['uid']))
  if str(results[0]) == ('(\'y\',)'):
    packaged[session['uid']] = packaged.get(session['uid']) - 1
    print('matched')
  print(results)
  print(packaged.get(session['uid']))
  cart[session['uid']].remove(item)
  return redirect(url_for('getItem', item=search))

@app.route("/removeItem/<category>/<item>")
def removeItemFromCategory(category, item):
  cursor.execute("SELECT packaged FROM food WHERE name=(%s)", (item,))
  results = cursor.fetchall()
  print(packaged.get(session['uid']))
  if str(results[0]) == ('(\'y\',)'):
    packaged[session['uid']] = packaged.get(session['uid']) - 1
    print('matched')
  print(results)
  print(packaged.get(session['uid']))
  cart[session['uid']].remove(item)
  return redirect(url_for('getItemsFromCategory', catg=category))

@app.route("/removeItemMain/<item>")
def removeItemFromMain(item):
  cursor.execute("SELECT packaged FROM food WHERE name=(%s)", (item,))
  results = cursor.fetchall()
  # ifprint(packaged.get(session['uid']))
  if str(results[0]) == ('(\'y\',)'):
    packaged[session['uid']] = packaged.get(session['uid']) - 1
    print('matched')
  print(results)
  print(packaged.get(session['uid']))
  cart[session['uid']].remove(item)
  return redirect(url_for('main'))

@app.route("/removeItemFavorites/<item>")
def removeItemFromFavorites(item):
  cursor.execute("SELECT packaged FROM food WHERE name=(%s)", (item,))
  results = cursor.fetchall()
  print(packaged.get(session['uid']))
  if str(results[0]) == ('(\'y\',)'):
    packaged[session['uid']] = packaged.get(session['uid']) - 1
    print('matched')
  print(results)
  print(packaged.get(session['uid']))
  cart[session['uid']].remove(item)
  return redirect(url_for('getFavorites'))

@app.route("/removeItemInfo/<item>")
def removeItemFromInfo(item):
  cursor.execute("SELECT packaged FROM food WHERE name=(%s)", (item,))
  results = cursor.fetchall()
  print(packaged.get(session['uid']))
  if str(results[0]) == ('(\'y\',)'):
    packaged[session['uid']] = packaged.get(session['uid']) - 1
    print('matched')
  print(results)
  print(packaged.get(session['uid']))
  cart[session['uid']].remove(item)
  return redirect(url_for('getInfo'))

if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 5000))
    app.run(debug=False, port=PORT, host='0.0.0.0')
