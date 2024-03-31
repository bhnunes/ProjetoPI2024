
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from dotenv import load_dotenv
import os
from flask import request, jsonify

# Load the .env file
load_dotenv()


app = Flask(__name__)

# MySQL connection configuration
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')

mysql = MySQL(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    return redirect(url_for('dashboard'))
     

@app.route('/dashboard')
def dashboard():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM sys.userinput")
    users = cursor.fetchall() # Fetch all rows from the query result
    return render_template('dashboard.html', users=users)



if __name__ == '__main__':
    app.run(debug=True)