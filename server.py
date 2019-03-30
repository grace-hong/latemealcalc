from flask import Flask, render_template
import os
import psycopg2
import subprocess

import os

app = Flask(__name__)

#'heroku config:get DATABASE_URL -a calculatemeal' to get the name of the database
DATABASE_URL = subprocess.run(["heroku", "config:get", "DATABASE_URL", "-a", "calculatemeal"])

conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cursor = conn.cursor()

@app.route("/")
def main():
    return render_template('index.html')

@app.route("/<item>")
def search(item):
    #cursor.execute("SELECT * FROM food WHERE foodname='%s'" % item)
    #query = cursor.fetchone()
    if query == None:
        html = "No such item was found"
    else:
        html = query[0] + " " + query[2]
    
    return html


if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 5000))
    app.run(debug=False, port=PORT, host='0.0.0.0')
