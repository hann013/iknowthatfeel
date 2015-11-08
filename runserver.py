"""
This script runs the FlaskWebProject application using a development server.
"""

from os import environ
from IKnowThatFeel import app,init_db
#from Models.user import User

init_db()
if __name__ == '__main__':
    HOST = environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT)
