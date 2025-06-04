from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'secret-key-change-it'

UPLOAD_FOLDER = 'static/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# إنشاء قاعدة بيانات
def init_db():
    with sqlite3.connect('patients.db') as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                national_id TEXT,
                phone TEXT,
                address TEXT,
                notes TEXT,
                photo_filename TEXT,
                report_filename TEXT
            )
        ''')
init_db()

USERS = {
    "doctor": "1234",
    "assistant": "0000"
}

@app.route('/')
def home():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in USERS and USERS[username] == password:
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            error = "بيانات الدخول غير صحيحة."
    return render_template('login.html', error=error)

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    with sqlite3.connect('patients.db') as conn:
        conn.row_factory = sqlite3.Row
        patients = conn.execute('SELECT * FROM patients ORDER BY id DESC').fetchall()

    return render_template('dashboard.html', patients=patients)

@app.route('/add', methods=['GET', 'POST'])
def add_patient():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form['name']
        national_id = request.form['national_id']
        phone = request.form['phone']
        address = request.form['address']
        notes = request.form['notes']

        photo = request.files['photo']
        report = request.files['report']

        photo_filename = secure_filename(photo.filename)
        report_filename = secure_filename(report.filename)

        photo.save(os.path.join(UPLOAD_FOLDER, photo_filename))
        report.save(os.path.join(UPLOAD_FOLDER, report_filename))

        with sqlite3.connect('patients.db') as conn:
            conn.execute('''
                INSERT INTO patients (name, national_id, phone, address, notes, photo_filename, report_filename)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (name, national_id, phone, address, notes, photo_filename, report_filename))

        return redirect(url_for('dashboard'))

    return render_template('add_patient.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)