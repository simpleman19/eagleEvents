from flask import Blueprint, render_template

events_blueprint = Blueprint('events', __name__)


@events_blueprint.route('/listEvents')
def list_events():
    # TODO LIST
    return render_template('event.html.j2')


@events_blueprint.route('/modifyEvent')
def modify_event():
    # TODO Modify
    return render_template('test.html.j2')


@events_blueprint.route('/seatingChart')
def seating_chart():
    # TODO Seating Chart
    # UI Seating Chart
    return render_template('test.html.j2')


@events_blueprint.route('/tableCards')
def table_cards():
    # TODO Table Cards
    return render_template('test.html.j2')


@events_blueprint.route('/attendanceList')
def attendance_list():
    # TODO Attendance List
    return render_template('test.html.j2')


@events_blueprint.route('/printSeatingChart')
def print_seating_chart():
    # Print Seating Chart
    # TODO Probably just return the pdf or whatever
    # May not actually need this but stubbing it anyway
    return render_template('test.html.j2')
