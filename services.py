from functools import wraps

from flask import g, session, current_app, redirect, url_for, request
from werkzeug.exceptions import HTTPException, HTTP_STATUS_CODES


def login_required(f):
    """
    redirects unauthenticated users
    :param func:
    :return:
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.get('user') is None:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


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


def is_json(value):
    """
    checks if a string is a JSON object
    :param value:
    :return:
    """
    try:
        result = json.loads(value)
        return True
    except ValueError, e:
        return False