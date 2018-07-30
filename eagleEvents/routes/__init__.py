from flask import Blueprint, render_template, g, redirect, url_for, session, request, jsonify, current_app as app
from eagleEvents.auth import multi_auth, create_token
import datetime

main_blueprint = Blueprint('main', __name__)


@main_blueprint.route('/', methods=['GET'])
@main_blueprint.route('/home', methods=['GET'])
@multi_auth.login_required
def home():
    return render_template('event.html.j2')


# Will handle UI login and logout in this file, everything else will be in a blueprint in another file

@main_blueprint.route('/login', methods=['GET'])
def login():
    if 'login_failed' in session and session['login_failed']:
        error_message = "Authentication Failure, please login again"
    else:
        error_message = ""
    # Reset login failure
    session['login_failed'] = False
    return render_template('login.html.j2', error_message=error_message)


@main_blueprint.route('/login', methods=['POST'])
@multi_auth.login_required
def login_user():
    if g.current_user is None:
        redirect(url_for('main.login'))
    else:
        token = create_token()
        resp = redirect(url_for('main.home'))
        resp.set_cookie('Bearer', token, expires=datetime.datetime.now() +
                                                 datetime.timedelta(hours=app.config['JWT_EXPIRATION_HOURS']))
        return resp


@main_blueprint.route('/logout', methods=['GET'])
def logout():
    resp = redirect(url_for('main.login'))
    resp.set_cookie('Bearer', '', expires=datetime.datetime.now())
    session['login_failed'] = False
    return resp


@main_blueprint.route('/testApi', methods=['GET', 'POST'])
@multi_auth.login_required
def test_api():
    return jsonify({ 'username': g.current_user.username })
