from flask import Blueprint, render_template
from ..printing.chart import seating_chart_print

events_blueprint = Blueprint('events', __name__)


@events_blueprint.route('/listEvents')
def list_events():
    # TODO LIST
    return render_template('test.html.j2')


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


@events_blueprint.route('/printSeatingChartTest')
def print_seating_chartTest():
    # test page for printing seating chart
    return render_template('print.html.j2')


@events_blueprint.route('/printSeatingChart/<id>', methods=['POST'])
def print_seating_chart(id):
    print('here in route')
    # Print Seating Chart
    seating_chart_print(id)
    return ''



    
