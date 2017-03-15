import logging
from datetime import date
import hashlib

from flask import Flask, render_template, request, redirect, g, flash, jsonify
from flask_restful import Api
from flask_swagger import swagger
from google.appengine.ext import ndb

from settings import Config
from models import Address, Booking, Customer, Room, User
from forms import LoginForm
from services import login_required

from resources import LoginResource

app = Flask('hotels')
app.config.from_object(Config)
app.api = Api(app, prefix='/v1')


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


@app.route('/', methods=['GET'])
@login_required
def index():
    return render_template('index.html', **locals())


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST':
        user = User.query(User.username == form.username.data).get()
        if user and user.check_password(form.password.data):
            g.user = user
            return redirect('index')
        else:
            flash('Invalid User/password combination')
    return render_template('login.html', **locals())


@app.route('/logout')
@login_required
def logout():
    g.user = None
    return redirect('index')


@app.route("/spec")
def spec():
    return jsonify(swagger(app, from_file_keyword='swagger_from_file'))


app.api.add_resource(LoginResource, '/login')