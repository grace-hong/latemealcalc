from flask import Flask, render_template
import os
#import mysql.connector


app = Flask(__name__)

conn = psycopg2.connect("dbname=inventory user=gracehong password=WoChiPingGuo4868")
cursor = conn.cursor()
#db = mysql.connector.connect(host = "localhost", user = "root", passwd = "pass")
#cursor = db.cursor()

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
