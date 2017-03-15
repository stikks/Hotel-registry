from flask_wtf import Form
from wtforms import SelectField, PasswordField, StringField, FloatField, BooleanField, IntegerField, DateField
from wtforms.validators import DataRequired, Optional, Email, EqualTo
from wtforms.fields.html5 import EmailField


class LoginForm(Form):
    """
    LoginForm to authenticate login request
    """
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])


class RegistrationForm(Form):
    """
    Registration form to create new users
    """
    # address information
    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])
    phone_number = StringField("Phone Number", validators=[DataRequired()])
    address = StringField("Address", validators=[DataRequired()])

    # authentication information
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])