from functools import wraps
from flask import g, session, current_app, redirect, url_for, request


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
