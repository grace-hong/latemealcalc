from flask import Flask, render_template
import os
import mysql.connector

app = Flask(__name__)

@app.route("/")
def main():
	db = mysql.connect {
		host = "localhost",
		user = "root",
		passwd = "pass"
	}
    return render_template('index.html')

if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 5000))
    app.run(debug=False, port=PORT, host='0.0.0.0')
