from website import app, conn, cursor, flm
from flask import render_template, request, flash, redirect, url_for, send_file, abort
from flask_login import login_user, current_user, logout_user, login_required, UserMixin
import os
import shutil
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin):
    
    def __init__(self, id, username, email, password):
        self.id = id
        self.username = username
        self.email = email
        self.password = password

@app.route('/')
def home():
    return render_template('home.html', user = current_user)

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form.get('username')
        psw = request.form.get('password')
        
        cursor.execute(f"SELECT * FROM USERS WHERE NAME = '{str(name)}'")
        user = cursor.fetchone()
        
        if user and check_password_hash(user[3], psw):
            us = User(user[0], user[1], user[2], user[3])
            login_user(us)
            return redirect(url_for('profile'))
        else:
            flash('Invalid username or password, try again!')
            
    return render_template('login.html')

@app.route('/signup', methods = ['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('username')
        email = request.form.get('email')
        psw = request.form.get('psw')
        cpsw = request.form.get('cpsw')
        
        cursor.execute("SELECT * FROM USERS")
        users = cursor.fetchall()
        
        for user in users:
            if name == user[1]:
                flash('Username already exists!', 'error')
                return redirect(url_for('signup'))
            if email == user[2]:
                flash('Email already exists!', 'error')
                return redirect(url_for('signup'))
        
        if psw == cpsw:
            hashed = generate_password_hash(psw)
            cursor.execute('INSERT INTO USERS(NAME, EMAIL, PASSWORD) VALUES(%s, %s, %s)', (name, email, hashed))
            conn.commit()
            
            cursor.execute(f"SELECT * FROM USERS WHERE NAME = '{str(name)}'")
            u = cursor.fetchone()
            us = User(u[0], u[1], u[2], u[3])
            login_user(us)
            return redirect(url_for('home'))
        else:
            flash("Password isn't equal!", "error")
    return render_template('signup.html')

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user = current_user)

@app.route('/files', methods = ['GET', 'POST'])
@login_required
def files():
    upload_folder = f"uploads/{current_user.id}"
    
    cursor.execute(f"CREATE TABLE IF NOT EXISTS USER_{current_user.id}_FILES(ID INT PRIMARY KEY AUTO_INCREMENT, FILENAME TEXT NOT NULL)")
    conn.commit()
    
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
        
    if request.method == 'POST':
        file = request.files['file']
        if file:
            fname = file.filename
            fpath = os.path.join(upload_folder, fname)
            file.save(fpath)
            
            cursor.execute(f"INSERT INTO USER_{current_user.id}_FILES(FILENAME) VALUES(%s)", (fname,))
            conn.commit()
            
    if request.method == 'GET':
        if request.args.get('delete'):
            cursor.execute(f"SELECT * FROM USER_{current_user.id}_FILES WHERE ID = {request.args.get('delete')}")
            file = cursor.fetchone()
            os.remove(upload_folder + "/" + str(file[1]))
            cursor.execute(f"DELETE FROM USER_{current_user.id}_FILES WHERE ID = {request.args.get('delete')}")
            conn.commit()
        if request.args.get('download'):
            cursor.execute(f"SELECT * FROM USER_{current_user.id}_FILES WHERE ID = {request.args.get('download')}")
            file = cursor.fetchone()
            save = os.path.join('../' + upload_folder, str(file[1]))
            return send_file(save, as_attachment=True)
            
    cursor.execute(f"SELECT * FROM USER_{current_user.id}_FILES")
    files = cursor.fetchall()
    return render_template('files.html', files = files, count = len(files))

@app.route('/logout')
@login_required
def logout():
    if str(request.args.get('del')) == 'true':
        cursor.execute(f"DELETE FROM USERS WHERE NAME = '{current_user.username}'")
        cursor.execute(f"DROP TABLE USER_{current_user.id}_FILES")
        conn.commit()
        try:
            shutil.rmtree(f"uploads/{current_user.id}")
        except OSError as e:
            print(e)
    logout_user()
    return redirect(url_for('home'))