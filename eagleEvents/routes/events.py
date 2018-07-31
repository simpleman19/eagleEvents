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
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in set(['csv'])


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
    return render_template('test.html.j2')


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


"""
    API endpoint to change guest seat
    Method: POST
    
    Allows user to manually move guests between tables and even swap guests if needed
    
    Expected JSON to move guest:
    {
        'selectedGuest' : '<UUID>'     # REQUIRED, This is the guest initially selected to move
        'destinationTable' : '<UUID>'  # REQUIRED, This is the table that the selected guest is moving to
        'otherGuest' : '<UUID:-1>'     # REQUIRED, This is used if swapping 2 guests, if moving to empty seat then '-1'
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
    json = request.json
    if not json:
        response['error'] = "Error, invalid json in request"
        return jsonify(response), 400
    if not json['selectedGuest'] and not json['destinationTable'] and not json['otherGuest']:
        response['error'] = "Missing required fields in request JSON"
        return jsonify(response), 400
    try:
        sel_guest: Guest = Guest.query.filter_by(id=json['selectedGuest']).one_or_none()
        if json['otherGuest'] == '-1':
            other_guest = None
            dest_table: Table = Table.query.filter_by(id=json['destinationTable']).one_or_none()
        else:
            other_guest: Guest = Guest.query.filter_by(id=json['otherGuest']).one_or_none()
            if other_guest:
                dest_table = other_guest.assigned_table
            else:
                dest_table = None
        if sel_guest and dest_table and (other_guest or json['otherGuest'] == '-1'):
            if other_guest:
                other_guest.assigned_table = sel_guest.assigned_table
            sel_guest.assigned_table = dest_table
            db.session.commit()
            response['success'] = "Successfully moved {} to table # {} and {} to table # {}"\
                .format(sel_guest.full_name, dest_table.number, other_guest.full_name, other_guest.assigned_table.number)
            return jsonify(response)
        else:
            response['error'] = 'Error finding table or a guest'
            return jsonify(response), 404
    except Exception:
        response['error'] = 'Error finding table or a guest, exception thrown'
        return jsonify(response), 404
    response['error'] = 'Congrats, you made it to a part of the code that I thought was unreachable, bad news is I probably don\'t know how'
    return jsonify(response), 500
