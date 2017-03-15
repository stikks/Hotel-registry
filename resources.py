import hashlib, json

from flask import g, request, make_response
from flask_restful import Resource, abort
from flask_httpauth import HTTPBasicAuth

from models import User
from forms import LoginForm, RegistrationForm

auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(username, password):
    user = User.query(User.username == username).get()

    if not user or not user.check_password(password):
        return False
    g.user = user
    return True


class LoginResource(Resource):
    """
    Login api resource
    """

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
        login get resouce.
        ---
        responses:
          405:
            description: Method not Allowed
        """
        abort(405)

    def post(self):
        """
        Post a user.
        ---
        tags:
          - users
        parameters:
          - in: formdata
            name: request form
        definitions:
          - schema:
              id: Pet
              required:
                - name
                - owner
              properties:
                name:
                  type: string
                  description: the pet's name
                owner:
                  $ref: '#/definitions/Owner'
          - schema:
              id: Owner
              required:
                - name
              properties:
                name:
                  type: string
                  description: the owner's name
        responses:
          200:
            description: Returns the specified pet
            $ref: '#/definitions/Pet'
        """
        form = LoginForm(csrf_enabled=False, formdata=request.form)
        print(form.errors)
        exit()
        user = User.query(User.username == form.username.data).get()
        if user and user.check_password(form.password.data):
            g.user = user
            _data_ = {"status": "success", "data": user}
            _data_ = json.dumps(_data_)
            resp = make_response(_data_, 200)
            resp.headers['Content-Type'] = "application/json"
            return resp

        _data_ = {"status": "failure", "message": "The provided user credentials are invalid."}
        _data_ = json.dumps(_data_)
        resp = make_response(_data_, 403)
        resp.headers['Content-Type'] = "application/json"
        return resp


class UserResource(Resource):
    """
    Create a new user
    ---
    tags:
      - users
    definitions:
      - schema:
          id: Group
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
            userID:
              description: userID for user
              schema:
                id: Address
                properties:
                  first_name:
                    type: string
                  last_name:
                    type: string
                  address:
                    type: string
                  phone_number:
                    type: string
                  userID:
                    type: string
            groups:
              type: array
              description: list of groups
              items:
                $ref: "#/definitions/Group"
    responses:
      201:
        description: User created
    """
