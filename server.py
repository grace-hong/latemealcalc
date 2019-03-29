from flask import Flask, render_template
import os
import psycopg2

import os

app = Flask(__name__)

DATABASE_URL = os.environ['postgres://gniojkvxziujuu:1c53b1d388891669097c66f2e618d42e31ffffa249aaaef45ccf72034503106c@ec2-184-73-153-64.compute-1.amazonaws.com:5432/d1ipk1vqr3fslq']

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
