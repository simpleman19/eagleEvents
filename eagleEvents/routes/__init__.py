from flask import Blueprint, render_template

main_blueprint = Blueprint('main', __name__)


@main_blueprint.route('/', methods=['GET'])
@main_blueprint.route('/home', methods=['GET'])
def home():
    return render_template('event.html.j2', test='"Test Argument to Page"')


# Will handle UI login and logout in this file, everything else will be in a blueprint in another file

@main_blueprint.route('/login', methods=['GET'])
def login():
    # TODO LOGIN
    return render_template('login.html.j2')


@main_blueprint.route('/logout', methods=['GET'])
def logout():
    # TODO LOGOUT
    return render_template('test.html.j2')
