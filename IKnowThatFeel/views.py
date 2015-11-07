"""
Routes and views for the flask application.
"""

import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
from contextlib import closing
from IKnowThatFeel import app
#from Models import User

@app.route('/')
@app.route('/home')
def home():
    """Renders the home page."""
    return render_template(
        'index.html',
        title='I Know That Feel'
    )

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        name_cursor=g.db.execute('select username from users where username=?',[request.form['username']])
        password_cursor = g.db.execute('select password from users where username=?',[request.form['username']])

        if name_cursor.fetchone() is not None:
            name=name_cursor.fetchone()[0]
            password=password_cursor.fetchone()[0]

        if name_cursor.fetchone() is None:
            error = 'Invalid username'
        elif password != request.form['password']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('home'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('home'))

@app.route('/new_user', methods=['GET','POST'])
def new_user():

    if request.method =='POST':
        g.db.execute('insert into users (username, password) values (?, ?)',
                     [request.form['username'], request.form['password']])
        g.db.commit()
        session['logged_in']=True
        print('New user was successfully created')
        return redirect(url_for('home'))
    return render_template('new_user.html')
