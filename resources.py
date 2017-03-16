import hashlib, json

from flask import g, request, make_response
from flask_restful import Resource, abort, fields, marshal
from flask_httpauth import HTTPBasicAuth
from werkzeug.exceptions import HTTPException, HTTP_STATUS_CODES
from google.appengine.ext import ndb

from models import User, Booking, Room, Customer
from forms import LoginForm, RegistrationForm, BookingForm, RoomForm, CustomerForm, UpdateForm

auth = HTTPBasicAuth()
admin_auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(username, password):
    user = User.query(User.username == username).get()

    if not user or not user.check_password(password):
        return False
    g.user = user
    return True


@admin_auth.verify_password
def verify_admin(username, password):
    user = User.query(User.username == username).get()

    if not user or not user.check_password(password) or not user.is_admin:
        return False
    g.user = user
    return True


class CustomException(HTTPException):
    def __init__(self, code, data, description=None, name=None):
        """
        custom model for handling HTTPExceptions
        :param code: Response Code
        :param description: Description of error
        """
        self.code = code
        self.data = data
        self.response_name = name
        self.description = description
        super(CustomException, self).__init__(code)

    @property
    def name(self):
        """The status name."""
        if self.response_name:
            return self.response_name
        return HTTP_STATUS_CODES.get(self.code, 'Unknown Error')

    def get_response(self, environ=None):
        """
        Update HTTPException response processing
        :param environment:
        :return:
        """
        resp = super(CustomException, self).get_response(environ)
        resp.status = "%s %s" % (self.code, self.name.upper())
        return resp


class BaseResource(Resource):
    """
    BaseResource class to implement common methods
    """

    @property
    def output_fields(self):
        """ Property function to always generate a clean base value for output fields """
        return {
            'id': fields.Integer,
            'date_created': fields.DateTime(dt_format='iso8601'),
            'date_modified': fields.DateTime(dt_format='iso8601')
        }

    def prepare_errors(self, errors):
        """
        Helper class to prepare errors for response
        """
        _errors = {}
        for k, v in errors.items():
            _res = [str(z) for z in v]
            _errors[str(k)] = _res

        return _errors

    def get(self):
        """
        GET request method
        To be re-initialized by child class
        ---
        responses:
          405:
            description: Method not Allowed
        :return:
        """
        abort(405)

    def post(self):
        """
        POST request method
        To be re-initialized by child class
        ---
        responses:
          405:
            description: Method not Allowed
        :return:
        """
        abort(405)

    def delete(self, obj_id):
        """
        DELETE request method
        To be re-initialized by child class
        ---
        responses:
          405:
            description: Method not Allowed
        :return:
        """
        abort(405)


class LoginResource(BaseResource):
    """
    Login api resource
    """
    resource_fields = {
        'userID': fields.String,
        'username': fields.String
    }

    def post(self):
        """
        login a user
        ---
        tags:
          - users
        definitions:
          - schema:
              id: User
              properties:
                name:
                type: string
                description: Authentication
        parameters:
          - in: body
            name: body
            schema:
              id: User
              required:
                - username
                - password
              properties:
                username:
                  type: string
                  description: username for user
                password:
                  description: password for user
                users:
                  type: array
                  description: list of users
                  items:
                    $ref: "#/definitions/User"
        responses:
          200:
        """

        form = LoginForm(request.form, csrf_enabled=False)

        if form.validate():
            user = User.query(User.username == form.username.data).get()
            if user and user.check_password(form.password.data):
                g.user = user
                output = self.output_fields
                output.update(self.resource_fields)
                return marshal(user, output), 200
            else:
                raise CustomException(code=400, description="The provided user credentials are invalid.",
                                      name='Validation Failed',
                                      data={'description': 'The provided user credentials are invalid.',
                                            'name': 'Validation Failed'})
        error_data = self.prepare_errors(form.errors)
        raise CustomException(code=400, description="The provided user credentials are invalid.",
                              name='Validation Failed', data=error_data)


class UserResource(BaseResource):
    """
    Create a new user
    ---
    tags:
      - users
    definitions:
      - schema:
          id: User
          properties:
            name:
             type: string
             description: Create User
    parameters:
      - in: body
        name: body
        schema:
          id: User
          required:
            - username
            - password
            - first_name
            - last_name
          optional:
            - address
            - phone_number
          properties:
            username:
              type: string
              description: username for user
            password:
              description: password for user
            first_name:
              type: string
              description: first name for user
            last_name:
              type: string
              description: last name for user
            address:
              description: address for user
            phone number:
              description: phone number for user
            users:
              type: array
              description: list of users
              items:
                $ref: "#/definitions/User"
    responses:
      201:
        description: User created
    """

    resource_fields = {
        'username': fields.String,
        'first_name': fields.String,
        'last_name': fields.String,
        'address': fields.String,
        'phone_number': fields.String
    }

    @admin_auth.login_required
    def get(self, obj_id=None):
        if not obj_id:
            query = User.query().fetch()
            output = self.output_fields
            output.update(self.resource_fields)

            resp = {
                'results': marshal(query, output)
            }

            return resp, 200

        try:
            user = User.get_by_id(int(obj_id))

            if not user:
                abort(404, message="User with key ({}) not found".format(obj_id))

            output = self.output_fields
            output.update(self.resource_fields)
            return marshal(user, output), 200
        except Exception:
            abort(404, message="User with key ({}) not found".format(obj_id))

    @admin_auth.login_required
    def post(self, obj_id=None):
        if obj_id:
            form = UpdateForm(request.form, csrf_enabled=False)
            if form.validate():
                user = User.get_by_id(int(obj_id))
                if not user:
                    abort(404, message="User with key ({}) not found".format(obj_id))

                user.first_name = form.first_name.data if form.first_name.data else user.first_name
                user.last_name = form.last_name.data if form.last_name.data else user.last_name
                user.phone_number = form.phone_number.data if form.phone_number.data else user.phone_number
                user.address = form.address.data if form.address.data else user.address

                output = self.output_fields
                output.update(self.resource_fields)
                return marshal(user, output), 200

        else:
            form = RegistrationForm(request.form, csrf_enabled=False)
            if form.validate():
                user = User(username=form.username.data, password=hashlib.md5(form.password.data).hexdigest(),
                            first_name=form.first_name.data, last_name=form.last_name.data,
                            phone_number=form.phone_number.data, address=form.address.data)
                user_key = user.put()
                user.id = str(user_key.id())
                user.put()
                output = self.output_fields
                output.update(self.resource_fields)
                return marshal(user, output), 201

        error_data = self.prepare_errors(form.errors)
        raise CustomException(code=400, name='Validation Failed', data=error_data)

    @admin_auth.login_required
    def delete(self, obj_id):
        """
        DELETE user account
        :param obj_id: user key id
        :return:
        """
        try:
            user = User.get_by_id(int(obj_id))
            user.key.delete()
            return {"status": "successfully deleted"}, 204
        except Exception:
            raise CustomException(code=400, name='Validation Failed', data={"description": 'DELETE failed for User with '
                                                                                           'key {}'.format(obj_id)})


class CustomerResource(BaseResource):
    """
    Create a new customer
    ---
    tags:
      - customers
    definitions:
      - schema:
          id: Customer
          properties:
            name:
             type: string
             description: Create Customer
    parameters:
      - in: body
        name: body
        schema:
          id: Customer
          required:
            - first_name
            - last_name
          optional:
            - address
            - phone_number
          properties:
            first_name:
              type: string
              description: first name for user
            last_name:
              type: string
              description: last name for user
            address:
              description: address for user
            phone number:
              description: phone number for user
            customers:
              type: array
              description: list of customers
              items:
                $ref: "#/definitions/Customer"
    responses:
      201:
        description: Customer created
    """

    resource_fields = {
        'first_name': fields.String,
        'last_name': fields.String,
        'address': fields.String,
        'phone_number': fields.String
    }

    @auth.login_required
    def get(self, obj_id=None):
        if not obj_id:
            query = Customer.query().fetch()
            output = self.output_fields
            output.update(self.resource_fields)

            resp = {
                'results': marshal(query, output)
            }

            return resp, 200

        try:
            customer = Customer.get_by_id(int(obj_id))

            if not customer:
                abort(404, message="Customer with key ({}) not found".format(obj_id))

            output = self.output_fields
            output.update(self.resource_fields)
            return marshal(customer, output), 200
        except Exception:
            abort(404, message="Customer with key ({}) not found".format(obj_id))

    @auth.login_required
    def post(self, obj_id=None):

        if obj_id:
            form = UpdateForm(request.form, csrf_enabled=False)
            if form.validate():
                customer = Customer.get_by_id(int(obj_id))
                if not customer:
                    abort(404, message="Customer with key ({}) not found".format(obj_id))

                customer.first_name = form.first_name.data if form.first_name.data else customer.first_name
                customer.last_name = form.last_name.data if form.last_name.data else customer.last_name
                customer.phone_number = form.phone_number.data if form.phone_number.data else customer.phone_number
                customer.address = form.address.data if form.address.data else customer.address

                output = self.output_fields
                output.update(self.resource_fields)
                return marshal(customer, output), 200
        else:
            form = CustomerForm(request.form, csrf_enabled=False)

            if form.validate():

                customer = User(first_name=form.first_name.data, last_name=form.last_name.data,
                                phone_number=form.phone_number.data, address=form.address.data)
                customer.put()
                output = self.output_fields
                output.update(self.resource_fields)
                return marshal(customer, output), 201

        error_data = self.prepare_errors(form.errors)
        raise CustomException(code=400, name='Validation Failed', data=error_data)

    @auth.login_required
    def delete(self, obj_id):
        """
        DELETE customer
        :param obj_id: customer id
        :return:
        """
        try:
            customer = Customer.get_by_id(int(obj_id))
            customer.key.delete()
            return {"status": "Customer with id - {} successfully deleted" % obj_id}, 204
        except Exception:
            raise CustomException(code=400, name='Validation Failed',
                                  data={"description": 'DELETE failed for Customer with '
                                                       'key {}'.format(obj_id)})


class RoomResource(BaseResource):
    """
    Create a new room
    ---
    tags:
      - rooms
    definitions:
      - schema:
          id: Room
          properties:
            name:
             type: string
             description: Create Room
    parameters:
      - in: body
        name: body
        schema:
          id: Room
          required:
            - number
          optional:
            - is_booked
          properties:
            number:
              type: integer
              description: room number
            rooms:
              type: array
              description: list of rooms
              items:
                $ref: "#/definitions/Room"
    responses:
      201:
        description: Room created
    """

    resource_fields = {
        'number': fields.String,
        'is_booked': fields.Boolean
    }

    @auth.login_required
    def get(self, obj_id=None):
        if not obj_id:
            query = Room.query().fetch()
            output = self.output_fields
            output.update(self.resource_fields)

            resp = {
                'results': marshal(query, output)
            }

            return resp, 200

        try:
            room = Room.get_by_id(int(obj_id))

            if not room:
                abort(404, message="Room with key ({}) not found".format(obj_id))

            output = self.output_fields
            output.update(self.resource_fields)
            return marshal(room, output), 200
        except Exception:
            abort(404, message="Room with key ({}) not found".format(obj_id))

    @auth.login_required
    def post(self, obj_id=None):
        form = RoomForm(request.form, csrf_enabled=False)
        if form.validate():
            if obj_id:
                room = Room.get_by_id(int(obj_id))
                if not room:
                    abort(404, message="Room with key ({}) not found".format(obj_id))

                room.number = form.number.data if form.number.data else room.number
                room.is_booked = form.is_booked.data if form.is_booked.data else room.is_booked

                output = self.output_fields
                output.update(self.resource_fields)
                return marshal(room, output), 200

            room = Room(number=form.number.data, is_booked=form.is_booked.data)
            room.put()
            output = self.output_fields
            output.update(self.resource_fields)
            return marshal(room, output), 201

        error_data = self.prepare_errors(form.errors)
        raise CustomException(code=400, name='Validation Failed', data=error_data)

    @auth.login_required
    def delete(self, obj_id):
        """
        DELETE booking
        :param obj_id: booking id
        :return:
        """
        try:
            room = Room.get_by_id(int(obj_id))
            room.key.delete()
            return {"status": "Room with id - {} successfully deleted" % obj_id}, 204
        except Exception:
            raise CustomException(code=400, name='Validation Failed',
                                  data={"description": 'DELETE failed for Room with '
                                                       'key {}'.format(obj_id)})


class BookingResource(BaseResource):
    """
    Create a new booking
    ---
    tags:
      - bookings
    definitions:
      - schema:
          id: Booking
          properties:
            name:
             type: string
             description: Create Booking
    parameters:
      - in: body
        name: body
        schema:
          id: Booking
          required:
            - customerID
            - room_number
          optional:
            - is_active
          properties:
            customerID:
              type: string
              description: id of customer
            room_number:
              type: integer
              description: room number to be booked
            bookings:
              type: array
              description: list of bookings
              items:
                $ref: "#/definitions/Booking"
    responses:
      201:
        description: Booking created
    """

    resource_fields = {
        'customerID': fields.String,
        'room_number': fields.String,
        'is_active': fields.Boolean
    }

    @auth.login_required
    def get(self, obj_id=None):
        """
        RETRIEVE OBJECT(S)
        :param obj_id:
        :return:
        """
        if not obj_id:
            query = Booking.query().fetch()
            output = self.output_fields
            output.update(self.resource_fields)

            resp = {
                'results': marshal(query, output)
            }

            return resp, 200

        try:
            booking = Booking.get_by_id(int(obj_id))

            if not booking:
                abort(404, message="Booking with key ({}) not found".format(obj_id))

            output = self.output_fields
            output.update(self.resource_fields)
            return marshal(booking, output), 200
        except Exception:
            abort(404, message="Booking with key ({}) not found".format(obj_id))

    @auth.login_required
    def post(self, obj_id=None):
        """
        CREATE/UPDATE booking object
        :param obj_id:
        :return:
        """
        form = BookingForm(request.form, csrf_enabled=False)
        if form.validate():
            if obj_id:
                booking = Booking.get_by_id(int(obj_id))
                if not booking:
                    abort(404, message="Booking with key ({}) not found".format(obj_id))

                booking.room_number = form.room_number.data if form.room_number.data else booking.room_number
                booking.customerID = form.customerID.data if form.customerID.data else booking.customerID
                booking.is_active = form.is_active.data if form.is_active.data else booking.is_active

                output = self.output_fields
                output.update(self.resource_fields)
                return marshal(booking, output), 200

            booking = Booking(customerID=form.customerID.data, room_number=form.room_number.data)
            booking.put()
            output = self.output_fields
            output.update(self.resource_fields)
            return marshal(booking, output), 201

        error_data = self.prepare_errors(form.errors)
        raise CustomException(code=400, name='Validation Failed', data=error_data)

    @auth.login_required
    def delete(self, obj_id):
        """
        DELETE booking
        :param obj_id: booking id
        :return:
        """
        try:
            booking = Booking.get_by_id(int(obj_id))
            booking.key.delete()
            return {"status": "Booking with id - {} successfully deleted" % obj_id}, 204
        except Exception:
            raise CustomException(code=400, name='Validation Failed',
                                  data={"description": 'DELETE failed for Booking with '
                                                       'key {}'.format(obj_id)})




