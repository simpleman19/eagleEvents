<<<<<<< HEAD
from flask import Blueprint, render_template, send_file, make_response, send_from_directory
from eagleEvents.printing.chart import seating_chart_print
=======
from pathlib import Path
from flask import Blueprint, render_template, Flask, flash, request, redirect, url_for, g
from eagleEvents.models.event import Event
from eagleEvents.models.company import Company
import os, config
from werkzeug.utils import secure_filename
from eagleEvents.auth import multi_auth
ALLOWED_EXTENSIONS = set(['csv'])
>>>>>>> dev

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




    
 