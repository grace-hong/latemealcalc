from flask import Flask, render_template, Markup
import os
import psycopg2
import subprocess

import os
import csv


app = Flask(__name__, static_url_path = "", static_folder = "static")

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
    packaged VARCHAR(50) NOT NULL
  )
  """)

with open('fooddb.csv', 'r') as f:
  next(f)
  cursor.copy_from(f, 'food', sep=',')
conn.commit()

#cursor.execute(
 #   """
  #  \copy food(name, price, category, count, time, packaged)
   # FROM 'fooddb.csv' DELIMITER ',' CSV HEADER
    #""")

@app.route("/")
def main():
    return render_template("index.html")

@app.route("/contact")
def getContact():
    return render_template("contact.html")

@app.route("/favorites")
def getFavorites():
    cursor.execute("SELECT name FROM food ORDER BY count DESC LIMIT 3")
    results = cursor.fetchall()
    retVal = ""
    for re in results:
      retVal += str(re[0]) + ", "

    return render_template("favorites.html", resultStr=retVal)

@app.route("/info")
def getInfo():
    return render_template("info.html")

@app.route("/search/item/<item>")
def getItem(item):
  cursor.execute("SELECT name, price FROM food")
  results = cursor.fetchall()
  retVal = ""
  pre = '<div class="shop-item"><span class="shop-item-title">'
  post_title = '</span><div class="shop-item-details"><span class="shop-item-price">$'
  post = '</span><button class="btn btn-primary shop-item-button fas fa-plus" type="button"></button></div></div>'
  if len(results) == 0:
    return "No results found."
  for re in results:
      if item.lower() in str(re[0]).lower():
        retVal = retVal + (pre + str(re[0]) + post_title + str(re[1]) + post)
        # retVal = retVal + str(re[0]) + "\n"
        cursor.execute("UPDATE food SET count=count+1 WHERE name='%s'" % str(re[0]))

  return render_template("results.html", resultList = Markup(retVal))


@app.route("/search/category/<catg>")
def getItemsFromCategory(catg):
  catg = str(catg)
  cursor.execute("SELECT name, price FROM food WHERE category ='%s'" % catg)
  results = cursor.fetchall()
  retVal = ""
  pre = '<div class="shop-item"><span class="shop-item-title">'
  post_title = '</span><div class="shop-item-details"><span class="shop-item-price">'
  post = '</span><button class="btn btn-primary shop-item-button fas fa-plus" type="button"></button></div></div>'
  if len(results) == 0:
    return "No results found for " + catg
  for re in results:
    retVal = retVal + (pre + str(re[0]) + post_title + str(re[1]) + post)
  
  return render_template("category.html", resultList = Markup(retVal))


if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 5000))
    app.run(debug=False, port=PORT, host='0.0.0.0')