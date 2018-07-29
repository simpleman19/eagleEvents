from flask import g, jsonify, session, current_app as app, Blueprint, request, redirect, url_for
from eagleEvents.http_auth import HTTPBasicAuth, HTTPTokenAuth, MultiAuth

import jwt
from datetime import datetime, timedelta

from . import db
from .models import User

auth_blueprint = Blueprint('auth', __name__)

basic_auth = HTTPBasicAuth()
basic_optional_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth('Bearer')
token_optional_auth = HTTPTokenAuth('Bearer')
multi_auth = MultiAuth(basic_auth, token_auth)
multi_optional_auth = MultiAuth(basic_optional_auth, token_optional_auth)


@basic_auth.verify_password
def verify_password(username, password):
    if not username or not password:
        if request.form and request.form['username']:
            user = User.query.filter_by(username=request.form['username']).one_or_none()
            if user and user.verify_password(request.form['password']):
                g.current_user = user
                return True
        return False
    user = User.query.filter_by(username=username).one_or_none()
    if user is None or not user.verify_password(password):
        return False
    g.current_user = user
    return True


@basic_auth.error_handler
def password_error():
    """Return a 401 error to the client."""
    # To avoid login prompts in the browser, use the "Bearer" realm.
    # TODO the json sometimes gets returned in the browser, need to have a more reliable way to check if api or if full page request
    if request.is_xhr:
        return (jsonify({'error': 'authentication required'}), 401,
                {'WWW-Authenticate': 'Bearer realm="Authentication Required"'})
    else:
        response = redirect(url_for('main.login'))
        response.status_code = 401
        return response


@basic_optional_auth.verify_password
def verify_optional_password(username, password):
    if not username or not password:
        if request.method == 'POST' and request.form['username']:
            user = User.query.filter_by(username=request.form['username']).one_or_none()
            if user.verify_password(request.form['password']):
                g.current_user = user
                return True
        g.current_user = None
        return True
    return verify_password(username, password)


@token_auth.verify_token
def verify_token(token, add_to_session=False):
    print(token)
    if add_to_session:
        if 'username' in session:
            del session['username']
    try:
        decoded = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        print('Expired')
        return False
    except jwt.DecodeError:
        print('Decode error')
        return False
    user_id = decoded['user_id']
    user = User.query.filter_by(id=user_id).one_or_none()
    if user is None:
        return False
    g.current_user = user
    if add_to_session:
        session['username'] = user.username
    return True


@token_auth.error_handler
def token_error():
    """Return a 401 error to the client."""
    # TODO the json sometimes gets returned in the browser, need to have a more reliable way to check if api or if full page request
    if request.is_xhr:
        return (jsonify({'error': 'authentication required'}), 401,
                {'WWW-Authenticate': 'Bearer realm="Authentication Required"'})
    else:
        response = redirect(url_for('main.login'))
        response.status_code = 401
        return response


@token_optional_auth.verify_token
def verify_optional_token(token):
    if token == '':
        g.current_user = None
        return True
    return verify_token(token)


@token_optional_auth.error_handler
def multi_error():
    """Return a 401 error to the client."""
    # TODO the json sometimes gets returned in the browser, need to have a more reliable way to check if api or if full page request
    if request.is_xhr:
        return (jsonify({'error': 'authentication required'}), 401,
            {'WWW-Authenticate': 'Bearer realm="Authentication Required"'})
    else:
        response = redirect(url_for('main.login'))
        response.status_code = 401
        return response


@auth_blueprint.route('/token', methods=['GET', 'POST'])
@multi_auth.login_required
def get_token():
    if g.current_user is None:
        return (jsonify({'error': 'authentication is required'}), 401,
                {'WWW-Authenticate': 'Bearer realm="Authentication Required"'})
    token = create_token()
    resp = jsonify({'token': token.decode('UTF-8')})
    return resp


def create_token():
    user = g.current_user
    if user is not None:
        return jwt.encode({'username': user.username,
                    'user_id': str(user.id.hex),
                    'exp': (datetime.utcnow() + timedelta(hours=24))
                    }, app.config['SECRET_KEY'], algorithm='HS256')
    else:
        return None