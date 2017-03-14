from flask_wtf import FlaskForm
from wtforms import SelectField, PasswordField, StringField, FloatField, BooleanField, IntegerField, DateField
from wtforms.validators import DataRequired, Optional, Email, EqualTo
from wtforms.fields.html5 import EmailField


class LoginForm():
    """
    LoginForm to authenticate login request
    """
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])