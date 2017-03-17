import hashlib, json

from flask import g, request, make_response
from flask_restful import Resource, abort, fields, marshal
from flask_httpauth import HTTPBasicAuth
from google.appengine.ext import ndb

from models import User, Booking, Room, Customer
from forms import LoginForm, RegistrationForm, BookingForm, RoomForm, CustomerForm, UpdateForm, UpdateBookingForm
from services import is_json, CustomException

auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(username, password):
    """
    HTTP Basic authentication
    :param username:
    :param password:
    :return:
    """
    user = User.query(User.username == username).get()

    if not user or not user.check_password(password):
        try:
            if g.user:
                return True
        except:
            return False
    g.user = user
    return True


class BaseResource(Resource):
    @property
    def output_fields(self):
        """
        default fields present in all model objects
        :return:
        """
        return {
            'id': fields.Integer,
            'date_created': fields.DateTime(dt_format='iso8601'),
            'date_modified': fields.DateTime(dt_format='iso8601')
        }

    def prepare_errors(self, errors):
        """
        prepares errors for response
        :param errors:
        :return:
        """
        _errors = {}
        for k, v in errors.items():
            _res = [str(z) for z in v]
            _errors[str(k)] = _res

        return _errors

    def prepare_data(self):
        """
        processes POST request data before form validation
        :return: form data
        """
        data = request.form.copy()
        if is_json(request.data):
            data.update(json.loads(request.data))

        return data

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

    @auth.login_required
    def put(self, obj_id):
        """
        PUT request method
        To be re-initialized by child class
        ---
        responses:
          405:
            description: Method not Allowed when obj_id is missing
        :return:
        """
        if not obj_id:
            abort(405, message="obj_id missing from request")

        return self.post(obj_id)

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
    resource_fields = {
        'first_name': fields.String,
        'last_name': fields.String,
        'address': fields.String,
        'phone_number': fields.String,
        'username': fields.String
    }

    def post(self):
        """
        Login an existing user
        ---
        tags:
          - login
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
                  type: string
                  description: password for user
        responses:
          201:
            description: User logged in
        """
        data = self.prepare_data()
        form = LoginForm(data, csrf_enabled=False)

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

    def put(self):
        """
        Not available for this resource
        :return:
        """
        abort(405)

    def delete(self):
        """
        Not available for this resource
        :return:
        """
        abort(405)


class UserResource(BaseResource):

    resource_fields = {
        'username': fields.String,
        'first_name': fields.String,
        'last_name': fields.String,
        'address': fields.String,
        'phone_number': fields.String
    }

    @auth.login_required
    def get(self, obj_id=None):
        """
        Gets user(s).
        Returns all users if no obj_id is passed
        ---
        tags:
          - users
        parameters:
          - in: path
            name: obj_id
        definitions:
          - schema:
              id: User
              required:
                - first_name
                - username
              optional:
                - last_name
                - address
                - phone_number
              properties:
                first_name:
                  type: string
                  description: the user's first name
                last_name:
                  type: string
                  description: the user's last name
                address:
                  type: string
                  description: the user's address
                phone_number:
                  type: string
                  description: the user's phone number
                username:
                  type: string
                  description: the user's username
        responses:
          200:
            description: Returns the specified user or a list of users
            $ref: '#/definitions/User'
        """
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

    @auth.login_required
    def post(self, obj_id=None):
        """
        Post user(s)
        Create a new user/ Update a user
        ---
        tags:
          - users
        parameters:
          - in: path
            name: obj_id
          - in: body
            name: body
            schema:
              id: User
              required:
                - username
                - password
                - first_name
              optional:
                - last_name
                - address
                - phone_number
              properties:
                username:
                  type: string
                  description: username for user
                first_name:
                  type: string
                  description: first name for user
                last_name:
                  type: string
                  description: last name for user
                address:
                  type: string
                  description: address for user
                phone_number:
                  type: string
                  description: phone number for user
                password:
                  type: string
                  description: password for user
        responses:
          201:
            description: User created
        """
        data = self.prepare_data()
        if obj_id:
            form = UpdateForm(data, csrf_enabled=False)
            if form.validate():
                user = User.get_by_id(int(obj_id))
                if not user:
                    abort(404, message="User with key ({}) not found".format(obj_id))

                user.first_name = form.first_name.data if form.first_name.data else user.first_name
                user.last_name = form.last_name.data if form.last_name.data else user.last_name
                user.phone_number = int(form.phone_number.data) if form.phone_number.data else user.phone_number
                user.address = form.address.data if form.address.data else user.address
                user.put()
                output = self.output_fields
                output.update(self.resource_fields)
                return marshal(user, output), 200

        else:
            form = RegistrationForm(data, csrf_enabled=False)
            if form.validate():
                user = User(username=form.username.data, password=hashlib.md5(form.password.data).hexdigest(),
                            first_name=form.first_name.data, last_name=form.last_name.data,
                            phone_number=int(form.phone_number.data), address=form.address.data)
                user.put()
                user.id = str(user.key.id())
                user.put()
                output = self.output_fields
                output.update(self.resource_fields)
                return marshal(user, output), 201

        error_data = self.prepare_errors(form.errors)
        raise CustomException(code=400, name='Validation Failed', data=error_data)

    @auth.login_required
    def delete(self, obj_id):
        """
        DELETE user
        Delete a user
        ---
        tags:
          - users
        parameters:
          - in: path
            name: obj_id
            schema:
              id: User
        responses:
          204:
            description: User deleted
        """
        try:
            user = User.get_by_id(int(obj_id))
            user.key.delete()
            return {"status": "successfully deleted"}, 204
        except Exception:
            raise CustomException(code=400, name='Validation Failed',
                                  data={"description": 'DELETE failed for User with '
                                                       'key {}'.format(obj_id)})


class CustomerResource(BaseResource):

    resource_fields = {
        'first_name': fields.String,
        'last_name': fields.String,
        'address': fields.String,
        'phone_number': fields.String
    }

    @auth.login_required
    def get(self, obj_id=None):
        """
        Gets customer(s).
        Returns all customers if no obj_id is passed
        ---
        tags:
          - customers
        parameters:
          - in: path
            name: obj_id
        definitions:
          - schema:
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
                  description: the customer's first name
                last_name:
                  type: string
                  description: the customer's last name
                address:
                  type: string
                  description: the customer's address
                phone_number:
                  type: string
                  description: the customer's phone number
        responses:
          200:
            description: Returns the specified customer or a list of customers
            $ref: '#/definitions/Customer'
        """
        if not obj_id:
            query = Customer.query().fetch()
            output = self.output_fields
            output.update(self.resource_fields)

            resp = {
                'results': marshal(query, output),
                'count': len(query)
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
        """
       Post customer(s)
       Create a new customer/ Update a customer
       ---
       tags:
         - customers
       parameters:
         - in: path
           name: obj_id
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
                 description: first name for customer
               last_name:
                 type: string
                 description: last name for customer
               address:
                 type: string
                 description: address for customer
               phone_number:
                 type: string
                 description: phone number for customer
       responses:
         201:
           description: Customer created
       """
        data = self.prepare_data()
        if obj_id:
            form = UpdateForm(data, csrf_enabled=False)
            if form.validate():
                customer = Customer.get_by_id(int(obj_id))
                if not customer:
                    abort(404, message="Customer with key ({}) not found".format(obj_id))

                customer.first_name = form.first_name.data if form.first_name.data else customer.first_name
                customer.last_name = form.last_name.data if form.last_name.data else customer.last_name
                customer.phone_number = form.phone_number.data if form.phone_number.data else customer.phone_number
                customer.address = form.address.data if form.address.data else customer.address
                customer.put()

                output = self.output_fields
                output.update(self.resource_fields)
                return marshal(customer, output), 200
            else:
                error_data = self.prepare_errors(form.errors)
                raise CustomException(code=400, name='Validation Failed', data=error_data)
        else:
            form = CustomerForm(data, csrf_enabled=False)

            if form.validate():
                customer = Customer(first_name=form.first_name.data, last_name=form.last_name.data,
                                phone_number=form.phone_number.data, address=form.address.data)
                customer.put()
                customer.id = str(customer.key.id())
                customer.put()
                output = self.output_fields
                output.update(self.resource_fields)
                return marshal(customer, output), 201

        error_data = self.prepare_errors(form.errors)
        raise CustomException(code=400, name='Validation Failed', data=error_data)

    @auth.login_required
    def delete(self, obj_id):
        """
        DELETE Customer
        Delete a customer
        ---
        tags:
          - users
        parameters:
          - in: path
            name: obj_id
            schema:
              id: Customer
        responses:
          204:
            description: Customer deleted
        """
        try:
            customer = Customer.get_by_id(int(obj_id))
            customer.key.delete()
            return True, 204
        except Exception:
            raise CustomException(code=400, name='Validation Failed',
                                  data={"description": 'DELETE failed for Customer with '
                                                       'key {}'.format(obj_id)})


class RoomResource(BaseResource):
    resource_fields = {
        'number': fields.String,
        'is_booked': fields.Boolean
    }

    @auth.login_required
    def get(self, obj_id=None):
        """
        Gets room(s).
        Returns all rooms if no obj_id is passed
        ---
        tags:
          - rooms
        parameters:
          - in: path
            name: obj_id
        definitions:
          - schema:
              id: Room
              required:
                - number
              optional:
                - is_booked
              properties:
                number:
                  type: string
                  description: the room's number
        responses:
          200:
            description: Returns the specified room or a list of rooms
            $ref: '#/definitions/Room'
        """
        if not obj_id:
            query = Room.query().fetch()
            output = self.output_fields
            output.update(self.resource_fields)

            resp = {
                'results': marshal(query, output),
                'count': len(query)
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
        """
       Post room(s)
       Create a new room/ Update a room
       ---
       tags:
         - rooms
       parameters:
         - in: path
           name: obj_id
         - in: body
           name: body
           schema:
             id: Room
             required:
               - number
             properties:
               number:
                 type: integer
                 description: room number
       responses:
         201:
           description: Room created
       """
        data = self.prepare_data()
        form = RoomForm(data, csrf_enabled=False)
        if form.validate():
            if obj_id:
                room = Room.get_by_id(int(obj_id))
                if not room:
                    abort(404, message="Room with key ({}) not found".format(obj_id))

                room.is_booked = form.is_booked.data if form.is_booked.data else room.is_booked
                room.put()

                output = self.output_fields
                output.update(self.resource_fields)
                return marshal(room, output), 200

            room = Room(number=form.number.data, is_booked=form.is_booked.data)
            room.put()
            room.id = str(room.key.id())
            room.put()
            output = self.output_fields
            output.update(self.resource_fields)
            return marshal(room, output), 201

        error_data = self.prepare_errors(form.errors)
        raise CustomException(code=400, name='Validation Failed', data=error_data)

    @auth.login_required
    def delete(self, obj_id):
        """
        DELETE room
        Delete a room
        ---
        tags:
          - rooms
        parameters:
          - in: path
            name: obj_id
            schema:
              id: Room
        responses:
          204:
            description: Room deleted
        """
        try:
            room = Room.get_by_id(int(obj_id))
            room.key.delete()
            return True, 204
        except Exception:
            raise CustomException(code=400, name='Validation Failed',
                                  data={"message": 'DELETE failed for Room with '
                                                   'key {}'.format(obj_id)})


class BookingResource(BaseResource):

    resource_fields = {
        'customerID': fields.String,
        'room_number': fields.String,
        'is_active': fields.Boolean
    }

    @auth.login_required
    def get(self, obj_id=None):
        """
        Gets booking(s).
        Returns all bookings if no obj_id is passed
        ---
        tags:
          - bookings
        parameters:
          - in: path
            name: obj_id
        definitions:
          - schema:
              id: Booking
              required:
                - customerID
                - room_number
              optional:
                - is_active
              properties:
                customerID:
                  type: string
                  description: the customer's id
                room_number:
                  type: integer
                  description: the room's number
                is_booked:
                  type: boolean
                  description: the room's booking status
        responses:
          200:
            description: Returns the specified booking or a list of bookings
            $ref: '#/definitions/Booking'
        """
        if not obj_id:
            query = Booking.query().fetch()
            output = self.output_fields
            output.update(self.resource_fields)

            resp = {
                'results': marshal(query, output),
                'count': len(query)
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
       Create a new booking/ Update a booking
       ---
       tags:
         - bookings
       parameters:
         - in: path
           name: obj_id
         - in: body
           name: body
           schema:
             id: Booking
             required:
               - room_number
               - customerID
             optional:
               - is_active
             properties:
               customerID:
                 type: string
                 description: customer id
               room_number:
                 type: integer
                 description: room number
               is_active:
                 type: boolean
                 description: room booked
       responses:
         201:
           description: Booking created
       """
        data = self.prepare_data()
        if obj_id:
            form = UpdateBookingForm(data, csrf_enabled=False)
            if form.validate():
                booking = Booking.get_by_id(int(obj_id))
                if not booking:
                    abort(404, message="Booking with key ({}) not found".format(obj_id))

                booking.is_active = form.is_active.data
                booking.put()

                room = Room.query(Room.number == booking.room_number).get()
                room.is_booked = True if booking.is_active is True else False
                room.put()

                output = self.output_fields
                output.update(self.resource_fields)
                return marshal(booking, output), 200

            error_data = self.prepare_errors(form.errors)
            raise CustomException(code=400, name='Validation Failed', data=error_data)

        else:
            form = BookingForm(data, csrf_enabled=False)
            if form.validate():
                booking = Booking(customerID=form.customerID.data, room_number=int(form.room_number.data),
                                  is_active=True)
                booking.put()
                booking.id = str(booking.key.id())
                booking.put()

                room = Room.query(Room.number == booking.room_number).get()
                room.is_booked = True if booking.is_active is True else False
                room.put()

                output = self.output_fields
                output.update(self.resource_fields)
                return marshal(booking, output), 201

            error_data = self.prepare_errors(form.errors)
            raise CustomException(code=400, name='Validation Failed', data=error_data)

    @auth.login_required
    def delete(self, obj_id):
        """
        DELETE booking
        Delete a booking
        ---
        tags:
          - bookings
        parameters:
          - in: path
            name: obj_id
            schema:
              id: Booking
        responses:
          204:
            description: Booking deleted
        """
        try:
            booking = Booking.get_by_id(int(obj_id))
            booking.key.delete()
            return {"status": "Booking with id - {} successfully deleted" % obj_id}, 204
        except Exception:
            raise CustomException(code=400, name='Validation Failed',
                                  data={"description": 'DELETE failed for Booking with '
                                                       'key {}'.format(obj_id)})
