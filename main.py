import logging, json
from datetime import date
import hashlib
from itertools import chain

from flask import Flask, render_template, request, redirect, g, flash, jsonify, url_for, session
from flask_restful import Api
from flask_swagger import swagger
from google.appengine.ext import ndb

from settings import Config
from models import Booking, Customer, Room, User
from forms import LoginForm, RegistrationForm
from services import login_required

from resources import LoginResource, UserResource, BookingResource, CustomerResource, RoomResource

app = Flask('hotels')
app.config.from_object(Config)
app.api = Api(app, prefix='/v1')

swag = swagger(app)
swag['info']['version'] = "1.0"
swag['info']['title'] = "Hotel Bookings API"


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


@app.before_request
def load_user():
    if session.get("user_id"):
        user = User.get_by_id(session["user_id"])
        g.user = user



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
            session['user_id'] = user.key.id()
            return redirect(url_for('index'))
        else:
            flash('Invalid User/password combination')
    return render_template('login.html', **locals())


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form, csrf_enabled=False)

    if request.method == 'POST':
        if form.validate():
            user = User(username=form.username.data, password=hashlib.md5(form.password.data).hexdigest(),
                        first_name=form.first_name.data, last_name=form.last_name.data,
                        phone_number=form.phone_number.data, address=form.address.data)
            user.put()
            user.id = str(user.key.id())
            user.put()
            return redirect(url_for('login'))
        else:
            flash(form.errors)
    return render_template('signup.html', **locals())


@app.route('/logout')
@login_required
def logout():
    del session['user_id']
    g.user = None
    return redirect(url_for('index'))


@app.route("/spec")
def spec():
    return jsonify(swag)


app.api.add_resource(LoginResource, '/login')
app.api.add_resource(UserResource, '/users', '/users/<string:obj_id>')
app.api.add_resource(CustomerResource, '/customers', '/customers/<string:obj_id>')
app.api.add_resource(BookingResource, '/bookings', '/bookings/<string:obj_id>')
app.api.add_resource(RoomResource, '/rooms', '/rooms/<string:obj_id>')