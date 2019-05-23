from flask import Flask, redirect, url_for, render_template, request, jsonify, session
import os
import sqlite3 as sql

app = Flask(__name__)

app.secret_key = 'my super secret key'.encode('utf-8')

path = os.getcwd()

DATABASE = path + '/database/project_app.db'

def write_to_db(email, password):
    with sql.connect(DATABASE) as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
        conn.commit()

def find_account(email):
    with sql.connect(DATABASE) as conn:
        cur = conn.cursor()
        t = (email,)
        cur.execute('SELECT * FROM users WHERE email=?', t)
        results = cur.fetchall()
        return results

def validate_account(email, password):
    with sql.connect(DATABASE) as conn:
        cur = conn.cursor()
        t = (email, password)
        cur.execute('SELECT * FROM users WHERE email=? AND password=?', t)
        results = cur.fetchall()
        return results

def update_account(email, first_name, last_name, birthday, favorite_band, zipcode):
    with sql.connect(DATABASE) as conn:
        cur = conn.cursor()
        t = (first_name, last_name, birthday, favorite_band, zipcode, email)
        cur.execute('UPDATE users SET first_name = ?, last_name = ?, birthday = ?, favorite_band = ?, zip_code = ? where email = ?', t)

@app.route('/')
def root():
    return redirect(url_for('index'))

@app.route('/welcome', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        session['email'] = email
        results = find_account(email)
        if not results:
            write_to_db(email, password)
        else:
            session.pop('email', None)
            return render_template('signup_failure.html', results=results, email=email)
        return render_template('info.html')
    return render_template('signup.html')

@app.route('/info', methods=['GET', 'POST'])
def info():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        birthday = request.form['birthday']
        favorite_band = request.form['favorite_band']
        zipcode = request.form['zipcode']
        update_account(session['email'], first_name, last_name, birthday, favorite_band, zipcode)
        return render_template('account.html', first_name=first_name)
    try:
        if request.method == 'GET' and session['email']:
            return render_template('info.html')
    except KeyError:
        return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        results = validate_account(email, password)
        if not results:
            return render_template('login_failure.html')
        else:
            session['email'] = email
            return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/forgotpassword', methods=['GET'])
def idiot():
    return render_template('idiot.html')

@app.route('/home', methods=['GET'])
def home():
    try:
        results = find_account(session['email'])
        session['first_name'] = results[0][3]
        return render_template('home.html', first_name=session['first_name'])
    except KeyError:
        return redirect(url_for('index'))

@app.route('/edit', methods=['GET', 'POST'])
def edit():
    return render_template('edit.html')

@app.route('/signout', methods=['GET'])
def signout():
    session.pop('email', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=3000)
