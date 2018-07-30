"""
flask_httpauth
==================
This module provides Basic and Digest HTTP authentication for Flask routes.
:copyright: (C) 2014 by Miguel Grinberg.
:license:   MIT, see LICENSE for more details.
"""

"""
Modified by Chance Turner
July 2018
:license: MIT LICENSE
"""

from functools import wraps
from hashlib import md5
from random import Random, SystemRandom
from flask import request, make_response, session
from werkzeug.datastructures import Authorization
import datetime

__version__ = '3.2.3'


class HTTPAuth(object):
    def __init__(self, scheme=None, realm=None):
        self.scheme = scheme
        self.realm = realm or "Authentication Required"
        self.get_password_callback = None
        self.auth_error_callback = None

        def default_get_password(username):
            return None

        def default_auth_error():
            return "Unauthorized Access"

        self.get_password(default_get_password)
        self.error_handler(default_auth_error)

    def get_password(self, f):
        self.get_password_callback = f
        return f

    def error_handler(self, f):
        @wraps(f)
        def decorated(*args, **kwargs):
            res = f(*args, **kwargs)
            res = make_response(res)
            if res.status_code == 200:
                # if user didn't set status code, use 401
                res.status_code = 401
            if 'WWW-Authenticate' not in res.headers.keys():
                res.headers['WWW-Authenticate'] = self.authenticate_header()
            return res
        self.auth_error_callback = decorated
        return decorated

    def authenticate_header(self):
        return '{0} realm="{1}"'.format(self.scheme, self.realm)

    def login_required(self, f):
        @wraps(f)
        def decorated(*args, **kwargs):
            auth = request.authorization
            if auth is None and 'Authorization' in request.headers:
                # Flask/Werkzeug do not recognize any authentication types
                # other than Basic or Digest, so here we parse the header by
                # hand
                try:
                    auth_type, token = request.headers['Authorization'].split(
                        None, 1)
                    auth = Authorization(auth_type, {'token': token})
                except ValueError:
                    # The Authorization header is either empty or has no token
                    pass

            # if the auth type does not match, we act as if there is no auth
            # this is better than failing directly, as it allows the callback
            # to handle special cases, like supporting multiple auth types
            if auth is not None and auth.type.lower() != self.scheme.lower():
                auth = None

            # Flask normally handles OPTIONS requests on its own, but in the
            # case it is configured to forward those to the application, we
            # need to ignore authentication headers and let the request through
            # to avoid unwanted interactions with CORS.
            if request.method != 'OPTIONS':  # pragma: no cover
                if auth and auth.username:
                    password = self.get_password_callback(auth.username)
                else:
                    password = None
                if not self.authenticate(auth, password):
                    # Clear TCP receive buffer of any pending data
                    request.data
                    resp = self.auth_error_callback()
                    resp.set_cookie('Bearer', '', expires=datetime.datetime.now())
                    session['login_failed'] = True
                    print('Cleared Cookies')
                    return resp

            return f(*args, **kwargs)
        return decorated

    def username(self):
        if not request.authorization:
            return ""
        return request.authorization.username


class HTTPBasicAuth(HTTPAuth):
    def __init__(self, scheme=None, realm=None):
        super(HTTPBasicAuth, self).__init__(scheme or 'Basic', realm)

        self.hash_password_callback = None
        self.verify_password_callback = None

    def hash_password(self, f):
        self.hash_password_callback = f
        return f

    def verify_password(self, f):
        self.verify_password_callback = f
        return f

    def authenticate(self, auth, stored_password):
        if auth:
            username = auth.username
            client_password = auth.password
        else:
            username = ""
            client_password = ""
        if self.verify_password_callback:
            return self.verify_password_callback(username, client_password)
        if not auth:
            return False
        if self.hash_password_callback:
            try:
                client_password = self.hash_password_callback(client_password)
            except TypeError:
                client_password = self.hash_password_callback(username,
                                                              client_password)
        return client_password is not None and \
            client_password == stored_password


class HTTPTokenAuth(HTTPAuth):
    def __init__(self, scheme='Bearer', realm=None):
        super(HTTPTokenAuth, self).__init__(scheme, realm)

        self.verify_token_callback = None

    def verify_token(self, f):
        self.verify_token_callback = f
        return f

    def authenticate(self, auth, stored_password):
        if auth:
            token = auth['token']
        elif request.cookies.get('Bearer'):
            token = request.cookies.get('Bearer')
        else:
            token = ""
        if self.verify_token_callback:
            return self.verify_token_callback(token)
        return False


class MultiAuth(object):
    def __init__(self, main_auth, *args):
        self.main_auth = main_auth
        self.additional_auth = args

    def login_required(self, f):
        @wraps(f)
        def decorated(*args, **kwargs):
            selected_auth = None
            if 'Authorization' in request.headers:
                try:
                    scheme, creds = request.headers['Authorization'].split(
                        None, 1)
                except ValueError:
                    # malformed Authorization header
                    pass
                else:
                    for auth in self.additional_auth:
                        if auth.scheme == scheme:
                            selected_auth = auth
                            break
            elif request.cookies.get('Bearer'):
                for auth in self.additional_auth:
                    if auth.scheme == 'Bearer':
                        selected_auth = auth
                        break
            if selected_auth is None:
                selected_auth = self.main_auth
            return selected_auth.login_required(f)(*args, **kwargs)
        return decorated