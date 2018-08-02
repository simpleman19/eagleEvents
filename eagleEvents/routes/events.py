from eagleEvents.printing.chart import seating_chart_print
from pathlib import Path
from flask import Blueprint, render_template, flash, request, redirect, url_for, g, jsonify
from eagleEvents.models.event import Event
from eagleEvents.models.guest import Guest
from eagleEvents.models.table import Table
from eagleEvents.models import db
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
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@events_blueprint.route('/modifyEvent', methods=['GET', 'POST'])
@multi_auth.login_required
def modify_event():
    # TODO get the event that is currenlty being modified
    event = Event.query.first()
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
        else:
            flash('File Type Not Accepted', category='error')

    return render_template('add-update-event.html.j2')


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


@events_blueprint.route('/printSeatingChartTest')
def print_seating_chartTest():
    # test page for printing seating chart
    return render_template('print.html.j2')


@events_blueprint.route('/printSeatingChart/<id>', methods=['POST'])
def print_seating_chart(id):
    # Print Seating Chart
    return seating_chart_print(id)


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


