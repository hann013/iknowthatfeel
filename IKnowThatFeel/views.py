"""
Routes and views for the flask application.
"""

from flask import render_template, request, redirect, jsonify
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

@app.route('/game')
def game():
	"""Renders the game page."""
	count = int(request.args["count"])
	emotions = ["Happy",  "Sad", "Angry", "Fear", "Surprise"]
	r = randint(0, len(emotions)) 

	if count <= 10:
		return render_template(
			'game.html',
			count=count,
			emotion=emotions[r]
			)
	else:
		return redirect('/home')

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

