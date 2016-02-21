from flask import render_template, request
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app

@app.route('/')
@app.route('/index')
def get_home():
    """Render the home page for the logged in user, if any"""
    logged_in = not current_user.is_anonymous
    display_name = (current_user.display if logged_in else 'Log in')
    logged_in_string = 'true' if logged_in else 'false'
    return render_template('index.html', display_name=display_name,
            logged_in=logged_in_string)
