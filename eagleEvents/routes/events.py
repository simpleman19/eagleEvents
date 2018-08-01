from pathlib import Path
from flask import Blueprint, render_template, Flask, flash, request, redirect, url_for, g
from eagleEvents.models.event import Event
from eagleEvents.models.customer import Customer
from eagleEvents.models.user import User
from eagleEvents import db
import os, config
from werkzeug.utils import secure_filename
from eagleEvents.auth import multi_auth
ALLOWED_EXTENSIONS = set(['csv'])

events_blueprint = Blueprint('events', __name__)


@events_blueprint.route('/listEvents')
@multi_auth.login_required
def list_events():
    # TODO LIST
    return render_template('event.html.j2')


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in set(['csv'])


@events_blueprint.route('/addEvent', methods=['GET', 'POST'])
@multi_auth.login_required
def add_event():
    event = None
    if request.method == 'GET':
        planner_list = User.query.all()
        customer_list = Customer.query.all()
        return render_template('add-update-event.html.j2', customers=customer_list, planners=planner_list,
                               cancel_redirect=url_for('events.list_events'))
    elif request.method == 'POST':
        if event is None:
            customer = request.form['customer']
            event = Event(customer)
        if request.form['submit'] == 'save':
            is_valid = validate_and_save(event, request)
            if is_valid:
                flash("{name} added".format(name=event.name), "success")
                return redirect(url_for('events.list_events'))
            else:
                return render_template('add-update-customer.html.j2', event=event,
                                       cancel_redirect=url_for('events.list_events'))
        elif request.form['cancel'] == 'cancel':
            redirect(url_for('events.list_events'))
        else:
            upload_file(request, event)
    else:
        return render_template('add-update-customer.html.j2', event=event,
                               cancel_redirect=url_for('events.list_events'))


@events_blueprint.route('/modifyEvent/<event_id>', methods=['GET', 'POST'])
@multi_auth.login_required
def modify_event(event_id):
    event = Event.query.get(event_id)
    if request.method == 'GET':
        return render_template('add-update-event.html.j2', event=event,
                               cancel_redirect=url_for('events.list_events'))
    elif request.method == 'POST' and request.files:
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

    return render_template('add-update-event.html.j2')


def upload_file(request, event):
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
    return render_template('test.html.j2')


@events_blueprint.route('/attendanceList')
@multi_auth.login_required
def attendance_list():
    # TODO Attendance List
    return render_template('test.html.j2')


@events_blueprint.route('/printSeatingChart')
@multi_auth.login_required
def print_seating_chart():
    # Print Seating Chart
    # TODO Probably just return the pdf or whatever
    # May not actually need this but stubbing it anyway
    return render_template('test.html.j2')


def validate_and_save(event, request):
    event.planner = User.query.get(request.form['planner'])
    event.name = request.form['name']
    event.time = request.form['time']
    event.is_done = True if request.form['status'] == "Done" else False
    event.venue = request.form['venue']
    event.percent_extra_seats = request.form['extra']
    event.company = g.current_user.company
    event.table_size = request.form['table_size']

    if event.name is None or len(event.name) == 0:
        flash("Name is required", "error")
        return False
    else:
        db.session.add(event)
        db.session.commit()
        return True
