import logging
from datetime import date

from flask import Flask, render_template, request
from models import Address, Booking, Customer, Room
from forms import LoginForm

app = Flask('hotels')


@app.context_processor
def context():
    """
    custom context processor that's inherited by all templates
    :return:
    """
    today = date.today()
    length = len
    minimum = min

    return locals()


@app.errorhandler(500)
def server_error(e):
    # Log the error and stacktrace.
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred.', 500


@app.route('/')
def index():
    return render_template('index.html', **locals())


@app.route('/login')
def login():
    form = LoginForm(csrf_enabled=False)
    return render_template('login.html', **locals())


@app.route('/logout')
def logout():
    pass

