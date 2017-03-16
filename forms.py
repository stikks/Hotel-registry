from flask_wtf import Form
from wtforms import SelectField, PasswordField, StringField, FloatField, BooleanField, IntegerField, DateField
from wtforms.validators import DataRequired, Optional, Email, InputRequired
from wtforms.fields.html5 import EmailField

from models import User, Customer


class LoginForm(Form):
    """
    LoginForm to authenticate login request
    """
    username = StringField('Username', validators=[Email(), InputRequired(message='This field is required')])
    password = PasswordField("Password", validators=[DataRequired()])

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False

        user = User.query(User.username == self.username.data).get()
        if user is None:
            self.username.errors.append('Unknown username')
            return False

        if not user.check_password(self.password.data):
            self.password.errors.append('Invalid password')
            return False

        self.user = user

        return True


class RegistrationForm(Form):
    """
    Registration form to create new users
    """
    # address information
    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[Optional()])
    phone_number = StringField("Phone Number", validators=[Optional()])
    address = StringField("Address", validators=[Optional()])

    # authentication information
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False

        user = User.query(User.username == self.username.data).get()
        if user:
            self.username.errors.append('User with username - {} already exists'.format(self.username.data))
            return False
        self.user = user

        return True


class BookingForm(Form):
    """
    Booking form to create new users
    """
    # address information
    customerID = StringField("CustomerID", validators=[DataRequired()])
    room_number = StringField("Room", validators=[DataRequired()])
    is_active = BooleanField("Is Active", default=True)


class RoomForm(Form):
    """
    Registration form to create new users
    """
    # address information
    number = IntegerField("Room Number", validators=[DataRequired()])
    is_booked = BooleanField("Is Booked", default=True)


class CustomerForm(Form):
    """
    CustomerForm to create new customers
    """
    # address information
    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])
    phone_number = StringField("Phone Number", validators=[Optional()])
    address = StringField("Address", validators=[Optional()])

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False

        customer = Customer.query(Customer.first_name == self.first_name.data,
                                  Customer.last_name == self.last_name.data).get()
        if customer:
            self.first_name.errors.append('Customer with name - {} {} already exists'.format(
                self.first_name.data, self.last_name.data))
            return False
        self.customer = customer

        return True


class UpdateForm(Form):
    """
    Update user/customer information
    """
    # address information
    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])
    phone_number = StringField("Phone Number", validators=[Optional()])
    address = StringField("Address", validators=[Optional()])

