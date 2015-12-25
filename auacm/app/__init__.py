from flask import Flask, Response
from flask.ext.socketio import SocketIO
from threading import Thread
import time

# Create the God-object `app` to be used everywhere
app = Flask(__name__)
app.config.from_pyfile('config.py') # not sure if this works
test_app = app.test_client()

# websockets setup
socketio = SocketIO(app)

# Initialize handler functions.
from app import util
from app import views
from app.modules.submission_manager import views
from app.modules.scoreboard_manager import views
from app.modules.blog_manager import views
from app.modules.problem_manager import views
