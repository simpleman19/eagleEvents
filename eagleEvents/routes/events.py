from flask import Blueprint, render_template, send_file, make_response, send_from_directory
from eagleEvents.printing.chart import seating_chart_print
from pathlib import Path
from flask import Blueprint, render_template, Flask, flash, request, redirect, url_for, g
from eagleEvents.models.event import Event
from eagleEvents.models.customer import Customer
from eagleEvents.models.user import User
from eagleEvents.models.company import TableSize
from eagleEvents import db
import os, config, datetime
from werkzeug.utils import secure_filename
from eagleEvents.auth import multi_auth
ALLOWED_EXTENSIONS = set(['csv'])

events_blueprint = Blueprint('events', __name__)


@events_blueprint.route('/listEvents')
@multi_auth.login_required
def list_events():
    # TODO LIST
    return render_template('event.html.j2')


@events_blueprint.route('/addEvent', methods=['GET', 'POST'])
@multi_auth.login_required
def add_event():
    planner_list = User.query.all()
    customer_list = Customer.query.all()
    sizes = TableSize.query.all()
    # create a new event on the first customer in the list
    event = Event(customer_list[0])
    # set the default time to 7 days from now at 7 PM
    time = datetime.datetime.now()
    time = time.replace(time.year, time.month, time.day+7, hour=19, minute=0)
    event.time = time
    # if the method is post, handle that the same way as modify event
    if request.method == 'POST':
        # let the function tell us how we should be directed
        handler = handle_post(event)
        # handle the redirection
        return handler
    # if this is GET, handle that for first time event creation
    return render_template('add-update-event.html.j2', event=event, sizes=sizes, planner=g.current_user,
                           customers=customer_list, planners=planner_list,
                           date=convert_time(event.time), cancel_redirect=url_for('events.list_events'))


@events_blueprint.route('/modifyEvent/<event_id>', methods=['GET', 'POST'])
@multi_auth.login_required
def modify_event(event_id):
    event = Event.query.get(event_id)
    planner_list = User.query.all()
    customer_list = Customer.query.all()
    sizes = TableSize.query.all()
    # if the method is post, handle that the same way as add event
    if request.method == 'POST':
        # let the function tell us how we should be directed
        handler = handle_post(event)
        # handle the redirection
        return handler
    # if this is GET, handle that for event modification
    return render_template('add-update-event.html.j2', event=event, sizes=sizes, planner=event.planner,
                           customers=customer_list, planners=planner_list,
                           date=convert_time(event.time), cancel_redirect=url_for('events.list_events'))


def handle_post(event):
    planner_list = User.query.all()
    customer_list = Customer.query.all()
    sizes = TableSize.query.all()
    button = request.form.get('button')

    if button == 'save':
        is_valid = validate_and_save(event, request)
        if is_valid:
            flash("{name} added".format(name=event.name), "success")
            return redirect(url_for('events.list_events'))
        else:
            return render_template('add-update-event.html.j2', event=event, sizes=sizes, planner=event.planner,
                                   customers=customer_list, planners=planner_list,
                                   date=convert_time(event.time), cancel_redirect=url_for('events.list_events'))
    elif button == 'cancel':
        redirect(url_for('events.list_events'))
    elif button == 'seat':
        return redirect(url_for('events.print_seating_chart', id=event.id))
    elif button == 'attendance':
        return redirect(url_for('events.attendance_list'))
    elif button == 'table':
        return redirect(url_for('events.table_cards'))
    else:
        is_valid = validate_and_save(event, request)
        if is_valid:
            upload_file(event, request)
        return render_template('add-update-event.html.j2', event=event, sizes=sizes, planner=event.planner,
                               customers=customer_list, planners=planner_list,
                               date=convert_time(event.time), cancel_redirect=url_for('events.list_events'))


def upload_file(event, request):
    # check if the post request has the file part
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    # if user does not select file, browser also
    # submit a empty part without filename
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        home = str(Path.home())
        path = os.path.join(home, filename)
        file.save(path)
        c = g.current_user.company
        c.process_guest_list(path, event)
        flash('Import Completed: ' + filename)
    else:
        flash('File Type Not Accepted', category='error')


@events_blueprint.route('/seatingChart')
@multi_auth.login_required
def seating_chart():
    # TODO Seating Chart
    # UI Seating Chart
    return render_template('seating-chart.html.j2')


@events_blueprint.route('/tableCards')
@multi_auth.login_required
def table_cards():
    # TODO Table Cards
    return render_template('test.html.j2', test='table_cards')


@events_blueprint.route('/attendanceList')
@multi_auth.login_required
def attendance_list():
    # TODO Attendance List
    return render_template('test.html.j2', test='attendance_list')


@events_blueprint.route('/printSeatingChartTest')
def print_seating_chartTest():
    # test page for printing seating chart
    return render_template('print.html.j2')


@events_blueprint.route('/printSeatingChart/<id>', methods=['POST'])
def print_seating_chart(id):
    # Print Seating Chart
    return seating_chart_print(id)


def validate_and_save(event, request):
    event.company = g.current_user.company
    event.planner = User.query.filter_by(id=request.form['planner']).one_or_none()
    event.customer = Customer.query.filter_by(id=request.form['customer']).one_or_none()
    event.name = request.form['name']
    event.venue = request.form['venue']
    # get the html form of the datetime
    date_in = request.form['time']
    # convert it into python datetime
    event.time = datetime.datetime(*[int(v) for v in date_in.replace('T', '-').replace(':', '-').split('-')])
    event.is_done = True if request.form['status'] == "Done" else False
    event.table_size = TableSize.query.filter_by(id=request.form['table_size']).one_or_none()
    event.percent_extra_seats = request.form['extra']

    if event.name is None or len(event.name) == 0:
        flash("Name is required", "error")
        return False
    elif event.venue is None or len(event.venue) == 0:
        flash("Venue is required", "error")
        return False
    elif event.time is None or event.time < datetime.datetime.now():
        flash("Valid Date and Time is required", "error")
        return False
    elif event.percent_extra_seats is None or len(event.percent_extra_seats) == 0:
        flash("Extra Seating Percentage is required", "error")
        return False
    else:
        db.session.add(event)
        db.session.commit()
        return True


def convert_time(time):
    time=str(time).replace(" ", "T")
    date = (time[:16]) if len(time) > 16 else time
    return date


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in set(['csv'])

