from flask import Blueprint, render_template
from eagleEvents import models
from eagleEvents.models.event import Event
main_blueprint = Blueprint('main', __name__)


@main_blueprint.route('/', methods=['GET'])
@main_blueprint.route('/home', methods=['GET'])
def home():
    c = models.Company()

    event = Event.query.filter_by(name='Test Event').first()
    c.process_guest_list('GuestLists/GuestList_3000_2_2.csv', event)
    return render_template('test.html.j2', test='"Test Argument to Page"')


# Will handle UI login and logout in this file, everything else will be in a blueprint in another file

@main_blueprint.route('/login', methods=['GET'])
def login():
    # TODO LOGIN
    return render_template('test.html.j2')


@main_blueprint.route('/logout', methods=['GET'])
def logout():
    # TODO LOGOUT
    return render_template('test.html.j2')
