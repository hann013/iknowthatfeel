"""
Routes and views for the flask application.
"""

import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash, redirect, jsonify
from contextlib import closing
from IKnowThatFeel import app
from random import randint
import indicoio, operator, uuid
import numpy as np
import matplotlib.pyplot as plt
from pylab import savefig

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
            session['username']=request.form['username']
            globalName=name[0]
            globalID=(g.db.execute('select id from users where username=?',[name[0]])).fetchone()[0]
            print globalID
            session['userid']=globalID
            print "session userid"
            print session['userid']
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

@app.route('/stats',methods=['GET'])
def stats():
    if not session.get('logged_in'):
        abort(401)

    cur = g.db.cursor()
    scoreList=[]
    # the result of a "cursor.execute" can be iterated over by row
    for row in cur.execute('select gameid,score,count(*) from playthrough where playerid=? group by gameid,score',[session['userid']]):
        print row
        scoreList.append(row)
    print scoreList

    zeroes=[]
    ones=[]
    pct=[]
    for x in range(0,len(scoreList)):
        if(scoreList[x][1]==0):
            zeroes.append(scoreList[x][2]*1.0)
        if(scoreList[x][1]==1):
            ones.append(scoreList[x][2]*1.0)
    print zeroes
    print ones
    for x in range(0,len(ones)):
        pct.append(ones[x]/(zeroes[x]+ones[x]))
    print pct

    n_groups = len(pct)
    fig, ax = plt.subplots()
    index = np.arange(n_groups)
    bar_width = 0.35
    opacity = 0.4
    rects1 = plt.bar(index, pct, bar_width,
                     alpha=opacity,
                     color='b',
                     label='Accuracy Percentage')

    plt.xlabel('Game')
    plt.ylabel('Percentage Correct')
    plt.title('Dank Graph of PWu')
    plt.legend()
    plt.tight_layout()
    savefig('IKnowThatFeel/static/content/graph.png')

    return render_template('stats.html')

@app.route('/game')
def game():
    """Renders the game page."""
    count = int(request.args["count"])

    if count == 1:
        session["game_id"] = str(uuid.uuid4())

    emotions = ["Happy",  "Sad", "Angry", "Fear", "Surprise"]
    r = randint(0, len(emotions)-1)
    if count <= 10:
        return render_template('game.html', count=count, emotion=emotions[r])
    else:
        return redirect('/home')

@app.route('/identifygame')
def identifygame():
    count = int(request.args["count"])

    if count == 1:
        session["game_id"] = str(uuid.uuid4())

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
        g.db.execute('insert into playthrough (score,playerid,gameid) values (?,?,?)',[1, session['userid'], session["game_id"]])
    else:
        result["feedback"] = "Not quite - try again!"
        g.db.execute('insert into playthrough (score,playerid,gameid) values (?,?,?)',[0, session['userid'], session["game_id"]])

    g.db.commit()
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
                g.db.execute('insert into playthrough (score,playerid,gameid) values (?,?,?)',[1, session['userid'], session["game_id"]])
            else:
                result["feedback"] = "Not quite - try again!"
                g.db.execute('insert into playthrough (score,playerid,gameid) values (?,?,?)',[0, session['userid'], session["game_id"]])
            g.db.commit()
            result[highestKey] = emotions[highestKey]
            return jsonify(result)

    highestKey = highestKeys[0]
    result[highestKey] = emotions[highestKey]
    return jsonify(result)
