"""
Routes and views for the flask application.
"""

import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash, redirect, jsonify
from contextlib import closing
from IKnowThatFeel import app
from random import randint
import indicoio, operator

@app.route('/')
@app.route('/home')
def home():
    """Renders the home page."""
    return render_template(
        'index.html',
        title='I Know That Feel'
    )
globalName=""
globalID=0
count=0
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        name_cursor=g.db.execute('select username from users where username=?',[request.form['username']])
        password_cursor = g.db.execute('select password from users where username=?',[request.form['username']])

        name=name_cursor.fetchone()
        password=password_cursor.fetchone()
        print name[0]
        print password[0]
        if name[0] is None:
            error = 'Invalid username'
        elif password[0] != request.form['password']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            globalName=name[0]
            globalID=(g.db.execute('select id from users where username=?',[name[0]])).fetchone()[0]
            print globalID
            flash('You were logged in')
            return redirect(url_for('home'))
    return render_template('index.html', error=error)

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

@app.route('/game', methods=['GET','POST'])
def game():

    if request.method=='POST':
        g.db.execute('insert into playthrough (score,playerid) values (?,?)',[count,globalID])
        g.db.commit()
        return render_template('index.html')
    #else:
    """Renders the game page."""
    count = int(request.args["count"])
    emotions = ["Happy",  "Sad", "Angry", "Fear", "Surprise"]
    r = randint(0, len(emotions)-1)
    if count <= 10:
		return render_template('game.html', count=count, emotion=emotions[r])
    else:
		return redirect('/home')

@app.route('/identifygame')
def identifygame():
    count = int(request.args["count"])

    if count <= 10:
        return render_template(
            'identifygame.html',
            count=count
            )
    else:
        return redirect('/home')

@app.route('/indicoChoice', methods=['POST'])
def indicoChoice():
	correctEmotion = request.form["correctEmotion"]
	userChoice = request.form["userChoice"]

	result = {}

	if userChoice == correctEmotion:
		result["feedback"] = "You are correct!"
	else:
		result["feedback"] = "Not quite - try again!"
	return jsonify(result)


@app.route('/indico', methods=['POST'])
def indico():
	indicoio.config.api_key = "3e19af4454ebe0932333aff84913d88d"
	gameCount = request.form["gameCount"]
	emotion = request.form["emotion"]
	photoUrl = request.form["photoUrl"]

	result = {}

	emotions = indicoio.fer(photoUrl, detect=True, sensitivity=0.4)[0]['emotions']

	highestVals = {}
	highestVals["happyVal"] = emotions["Happy"] + emotions["Neutral"]
	highestVals["sadVal"] = emotions["Sad"] + emotions["Angry"]
	highestVals["fearVal"] = emotions["Fear"] + emotions["Surprise"]

	highestValsKey = max(highestVals.iteritems(), key=operator.itemgetter(1))[0]
	highestKeys = max(emotions.iteritems(), key=operator.itemgetter(1))

	for highestKey in highestKeys:
		if (highestKey == "Happy" or highestKey == "Neutral" and highestValsKey == "happyVal") or (highestKey == "Sad" or highestKey == "Angry" and highestValsKey == "sadVal") or (highestKey == "Fear" or highestKey == "Surprise" and highestValsKey == "fearVal"):
			if highestKey == emotion:
				result["feedback"] = "You are correct!"
			else:
				result["feedback"] = "Not quite - try again!"
			result[highestKey] = emotions[highestKey]
			return jsonify(result)

	highestKey = highestKeys[0]
	result[highestKey] = emotions[highestKey]
	return jsonify(result)
