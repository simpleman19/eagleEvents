from eagleEvents.printing.chart import seating_chart_print
from eagleEvents.printing.card import table_card_print
from eagleEvents.printing.attendance import attendance_list_print
import datetime
import os
from pathlib import Path

from flask import Blueprint, render_template, flash, request, redirect, url_for, g, jsonify, abort
from werkzeug.utils import secure_filename

from eagleEvents import db
from eagleEvents.auth import multi_auth
from eagleEvents.models.company import TableSize
from eagleEvents.models.customer import Customer
from eagleEvents.models.event import Event
from eagleEvents.models.guest import Guest
from eagleEvents.models.user import User
from eagleEvents.printing.chart import seating_chart_print

events_blueprint = Blueprint('events', __name__)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in set(['csv'])


@events_blueprint.route('/listEvents')
@multi_auth.login_required
def list_events():
    show_all = request.args.get("show_all")
    company_id_user = g.current_user.company_id
    events_of_company = Event.query.filter_by(company_id = company_id_user).order_by(Event.time.desc())
    if show_all is not None:
        events = events_of_company
    else:
        events = events_of_company.filter_by(planner_id = g.current_user.id, is_done = False)
    return render_template('event.html.j2', events=events, currentUser = g.current_user)


@events_blueprint.route('/addEvent', methods=['GET', 'POST'])
@multi_auth.login_required
def add_event():
    user_company_id = g.current_user.company.id
    planner_list = User.query.filter_by(company_id=user_company_id).all()
    customer_list = Customer.query.filter_by(company_id=user_company_id).all()
    sizes = TableSize.query.filter_by(company_id=user_company_id).all()
    # create a new event on the first customer in the list
    event = Event(customer_list[0])
    # set the default time to 7 days from now at 7 PM
    time = datetime.datetime.now()
    time = time.replace(time.year, time.month, time.day+7, hour=19, minute=0)
    event.time = time
    # if the method is post, handle that the same way as modify event
    if request.method == 'POST':
        # let the function tell us how we should be directed
        handler = handle_post(event, True)
        # handle the redirection
        return handler
    # if this is GET, handle that for first time event creation
    return render_template('add-update-event.html.j2', event=event, sizes=sizes, planner=g.current_user,
                           customers=customer_list, planners=planner_list, new=True, imported=False,
                           date=convert_time(event.time), cancel_redirect=url_for('events.list_events'))


@events_blueprint.route('/modifyEvent/<event_id>', methods=['GET', 'POST'])
@multi_auth.login_required
def modify_event(event_id):
    user_company_id = g.current_user.company.id
    event = Event.query.get(event_id)
    planner_list = User.query.filter_by(company_id=user_company_id).all()
    customer_list = Customer.query.filter_by(company_id=user_company_id).all()
    sizes = TableSize.query.filter_by(company_id=user_company_id).all()
    imported = True if Guest.query.filter_by(event_id=event.id).count() > 0 else False
    # if the method is post, handle that the same way as add event
    if request.method == 'POST':
        # let the function tell us how we should be directed
        handler = handle_post(event, False)
        # handle the redirection
        return handler
    # if this is GET, handle that for event modification
    return render_template('add-update-event.html.j2', event=event, sizes=sizes, planner=event.planner,
                           customers=customer_list, planners=planner_list, new=False, imported=imported,
                           date=convert_time(event.time), cancel_redirect=url_for('events.list_events'))


def handle_post(event, new):
    user_company_id = g.current_user.company.id
    planner_list = User.query.filter_by(company_id=user_company_id).all()
    customer_list = Customer.query.filter_by(company_id=user_company_id).all()
    sizes = TableSize.query.filter_by(company_id=user_company_id).all()
    button = request.form.get('button')
    imported = True if Guest.query.filter_by(event_id=event.id).count() > 0 else False
    if button == 'save':
        errors = Event.validate_and_save(event, request.form)
        if len(errors) == 0:
            if new:
                flash("{name} added".format(name=event.name), "success")
            else:
                flash("{name} updated".format(name=event.name), "success")
            return redirect(url_for('events.list_events'))
        else:
            for error in errors:
                flash(error, 'error')
            return render_template('add-update-event.html.j2', event=event, sizes=sizes, planner=event.planner,
                                   customers=customer_list, planners=planner_list, new=new, imported=imported,
                                   date=convert_time(event.time), cancel_redirect=url_for('events.list_events'))
    elif button == 'cancel':
        return redirect(url_for('events.list_events'))
    elif button == 'seat':
        return redirect(url_for('events.seating_chart', event_id=event.id))
    elif button == 'attendance':
        return redirect(url_for('events.attendance_list', id=event.id))
    elif button == 'table':
        return redirect(url_for('events.table_cards', id=event.id))
    else:
        errors = Event.validate_and_save(event, request.form)
        if len(errors) == 0:
            upload_file(event, request)
            imported = True
        else:
            for error in errors:
                flash(error, 'error')
        return render_template('add-update-event.html.j2', event=event, sizes=sizes, planner=event.planner,
                               customers=customer_list, planners=planner_list, new=new, imported=imported,
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


@events_blueprint.route('/seatingChart/<event_id>', methods=['GET', 'POST'])
@multi_auth.login_required
def seating_chart(event_id):
    # UI Seating Chart
    event = None
    try:
        event = Event.query.filter_by(id=event_id).one_or_none()
    except Exception:
        abort(404)
    if event is None:
        abort(404)
    return render_template('seating-chart.html.j2', tables=sorted(event.tables, key=lambda x: x.number))


@events_blueprint.route('/tableCards/<id>', methods=['GET', 'POST'])
@multi_auth.login_required
def table_cards(id):
    # Print table cards
    return table_card_print(id)


@events_blueprint.route('/attendanceList/<id>', methods=['GET', 'POST'])
@multi_auth.login_required
def attendance_list(id):
    # Print Seating Chart
    return attendance_list_print(id)


@events_blueprint.route('/printSeatingChartTest')
def print_seating_chartTest():
    # test page for printing seating chart
    return render_template('print.html.j2')


@events_blueprint.route('/printSeatingChart/<id>', methods=['GET', 'POST'])
def print_seating_chart(id):
    # Print Seating Chart
    return seating_chart_print(id)


def convert_time(time):
    time=str(time).replace(" ", "T")
    date = (time[:16]) if len(time) > 16 else time
    return date
