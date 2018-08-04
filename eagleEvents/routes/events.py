from eagleEvents.printing.chart import seating_chart_print
from pathlib import Path
from flask import Blueprint, render_template, flash, request, redirect, url_for, g, jsonify, abort
from eagleEvents.models.event import Event
from eagleEvents.models.customer import Customer
from eagleEvents.models.user import User
from eagleEvents.models.table import Table
from eagleEvents.models.company import TableSize
from eagleEvents.models.guest import Guest
from eagleEvents.auth import multi_auth
from eagleEvents import db
import os, config, datetime
from werkzeug.utils import secure_filename

events_blueprint = Blueprint('events', __name__)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in set(['csv'])


@events_blueprint.route('/listEvents')
@multi_auth.login_required
def list_events():
    show_all = request.args.get("show_all")
    currentUser = g.current_user
    company_id_user = currentUser.company_id
    events_of_company = Event.query.filter_by(company_id = company_id_user).order_by(Event.time.desc())
    if show_all is not None:
        events = events_of_company
    else:
        events = events_of_company.filter_by(planner_id = currentUser.id)
    return render_template('event.html.j2', events=events, currentUser = currentUser)


@events_blueprint.route('/modifyEvent', methods=['GET', 'POST'])
@multi_auth.login_required
def modify_event():
    # TODO get the event that is currenlty being modified
    event = Event.query.first()
    print("Modifying: " + str(event.id))
    if request.method == 'POST' and request.files:
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
    event = Event.query.get(event_id)
    planner_list = User.query.all()
    customer_list = Customer.query.all()
    sizes = TableSize.query.all()
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
    planner_list = User.query.all()
    customer_list = Customer.query.all()
    sizes = TableSize.query.all()
    button = request.form.get('button')
    imported = True if Guest.query.filter_by(event_id=event.id).count() > 0 else False
    if button == 'save':
        is_valid = validate_and_save(event, request)
        if is_valid:
            flash("{name} added".format(name=event.name), "success")
            return redirect(url_for('events.list_events'))
        else:
            return render_template('add-update-event.html.j2', event=event, sizes=sizes, planner=event.planner,
                                   customers=customer_list, planners=planner_list, new=new, imported=imported,
                                   date=convert_time(event.time), cancel_redirect=url_for('events.list_events'))
    elif button == 'cancel':
        return redirect(url_for('events.list_events'))
    elif button == 'seat':
        return redirect(url_for('events.seating_chart', event_id=event.id))
    elif button == 'attendance':
        return redirect(url_for('events.attendance_list'))
    elif button == 'table':
        return redirect(url_for('events.table_cards'))
    else:
        is_valid = validate_and_save(event, request)
        if is_valid:
            upload_file(event, request)
            imported = True
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
    # TODO Seating Chart
    # UI Seating Chart
    event = Event.query.filter_by(id="b45e38e0004946718126bd72446b76d3").one_or_none()
    return render_template('seating-chart.html.j2', tables=event.tables)


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


"""
    API endpoint to change guest seat
    Method: POST
    
    Allows user to manually move guests between tables and even swap guests if needed
    
    Expected JSON to move guest to open seat:
    {
        'selectedGuest' : '<UUID>'     # REQUIRED, This is the guest initially selected to move
        'destinationTable' : '<UUID>'  # REQUIRED, This is the table that the selected guest is moving to
    }
    
    Expected JSON to swap guests
    {
        'selectedGuest' : '<UUID>'     # REQUIRED, This is the guest initially selected to move
        'otherGuest' : '<UUID>'     # REQUIRED, This is used if swapping 2 guests
    }

    Response JSON:
    {
        'error' : '<This field will contain any error messages to show user>'
        'success' : '<This field will contain any success messages to show user>'
    }
"""
@events_blueprint.route('/changeSeat', methods=['POST'])
@multi_auth.login_required
def change_seats():
    response = {
        'error': '',
        'success': ''
    }
    return_code = 500
    json = request.json
    # Validate JSON
    if not json:
        response['error'] = "Error, invalid json in request"
        return jsonify(response), 400
    if not (('selectedGuest' in json and 'destinationTable' in json) or ('selectedGuest' in json and 'otherGuest' in json)):
        response['error'] = "Missing required fields in request JSON"
        return jsonify(response), 400
    try:
        # Find guest
        sel_guest: Guest = Guest.query.filter_by(id=json['selectedGuest']).one_or_none()
        # Find table if not swapping
        if 'otherGuest' not in json:
            other_guest = None
            dest_table: Table = Table.query.filter_by(id=json['destinationTable']).one_or_none()
        # Find other guests and get table from other guest
        else:
            other_guest: Guest = Guest.query.filter_by(id=json['otherGuest']).one_or_none()
            # Ensure other guest is found before trying to get table
            if other_guest:
                dest_table = other_guest.assigned_table
            else:
                dest_table = None  # This will break next if statement if table or guest not found
        # Ensure everything was found in database
        if sel_guest and dest_table and (other_guest or 'otherGuest' not in json):
            # Ensure guests and tables are all part of the same event
            if sel_guest.event_id != dest_table.event_id or (other_guest and sel_guest.event_id != other_guest.event_id):
                response['error'] = "Guests and tables are not part of the same event"
                return_code = 400
                return jsonify(response), return_code

            # If swapping then move other guest
            if other_guest:
                other_guest.assigned_table = sel_guest.assigned_table

            # Swap main guests
            sel_guest.assigned_table = dest_table
            db.session.commit()

            # Return message depending on whether it was a swap or not
            if other_guest:
                response['success'] = "Successfully moved {} to table # {} and {} to table # {}"\
                    .format(sel_guest.full_name, dest_table.number, other_guest.full_name, other_guest.assigned_table.number)
            else:
                response['success'] = "Successfully moved {} to table # {}" \
                    .format(sel_guest.full_name, dest_table.number)
            return_code = 200
        else:
            response['error'] = 'Error finding table or a guest'
            return_code = 404
        return jsonify(response), return_code
    # If anything threw an exception (Probably a filter_by statement)
    except Exception:
        response['error'] = 'Error finding table or a guest, exception thrown'
        return jsonify(response), 404


@events_blueprint.route('/api/table/guests', methods=['GET'])
@multi_auth.login_required
def get_guests_for_table():
    table_id = request.args.get('table')
    response = {
        'guests': []
    }
    if table_id is not None:
        try:
            table = Table.query.filter_by(id=table_id).one_or_none()
            if table is not None:
                response['guests'] = [{'full_name': g.full_name, 'id': str(g.id)} for g in table.guests]
                return jsonify(response), 200
            else:
                return jsonify({'error': 'Error finding table'}), 404
        # If anything threw an exception (Probably a sql statement)
        except Exception:
            return jsonify({'error': 'Error finding table, exception thrown'}), 404
    else:
        abort(404)

