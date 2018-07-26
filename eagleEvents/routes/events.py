from flask import Blueprint, render_template, Flask, flash, request, redirect, url_for
from eagleEvents.models.event import Event
from eagleEvents.models.company import Company
import os
from werkzeug.utils import secure_filename
UPLOAD_FOLDER = '/tmp'
ALLOWED_EXTENSIONS = set(['csv'])
events_blueprint = Blueprint('events', __name__)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@events_blueprint.route('/listEvents/<filename>')
def list_events(filename):
    # TODO LIST
    c = Company()
    event = Event.query.filter_by(name='Test Event').first()
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    c.process_guest_list(path, event)
    return render_template('test.html.j2', test=filename)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@events_blueprint.route('/upload', methods=['GET', 'POST'])
def upload_file():
    event = Event.query.filter_by(name='Test Event').first()
    if request.method == 'POST':
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
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(path)
            print(path)
            return redirect(url_for('events.list_events', filename=filename))

    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <p><input type=file onchange="this.form.submit()" name=file>
    </form>
    '''


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
