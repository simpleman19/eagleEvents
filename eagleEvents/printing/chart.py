import sys
import os
import datetime
from io import BytesIO
from flask import make_response, send_file, send_from_directory
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from eagleEvents.models import Company, Customer, Event, Table, Guest, SeatingPreferenceTable, SeatingPreference, User
from eagleEvents import db



def seating_chart_print(id_event):
    e = Event.query.filter(Event.id == id_event)[0]
    tables = Table.query.filter(Table.event_id == id_event)
    guests = Guest.query.filter(Guest.event_id == id_event)
    directory = os.path.join(os.getcwd(), 'temp')
    file_name = 'seatingChart.pdf'

    c = canvas.Canvas(os.path.join(directory , file_name))

    c.setLineWidth(.3)
    c.setFont("Helvetica", 12)
    # header
    c.drawString(30,750,"Eagles Events")
    c.drawString(30,735, e.name)
    year, month, day = str(e.time.date()).split("-")
    hour, min, second = str(e.time.time()).split(":")
    c.drawString(400,750,"Event Date: " + month + "/" + day + "/" + year)
    c.drawString(400,735,"Event Time: " +  hour + ":" + min)
    # title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(250,700,"Seating Chart")
    c.setFont("Helvetica", 12)
    # chart
    x = 40
    y = 370
    for t in tables:
        guests_for_table = guests.filter(Guest.table_id == t.id)
        guests_for_table = guests_for_table.order_by(Guest.last_name)
        c.roundRect(x, y, 250, 300, 4, stroke=1, fill=0)
        shift_x = 10
        shift_y = 275
        c.setFont("Helvetica-Bold", 12)
        c.drawString(x + shift_x, y + shift_y, "Table " + str(t.number))
        shift_y += -20
        c.drawString(x + shift_x, y + shift_y, "Last Name  ")
        c.drawString(x + shift_x + 90, y + shift_y, "First Name  ")
        c.drawString(x + shift_x + 180, y + shift_y, "Title")
        shift_y += -20
        c.setFont("Helvetica", 10)
        for guest in guests_for_table:
            c.drawString(x + shift_x, y + shift_y, guest.last_name)
            c.drawString(x + shift_x + 90, y + shift_y, guest.first_name)
            c.drawString(x + shift_x + 180, y + shift_y, guest.title)
            shift_y += -20
        c.setFont("Helvetica", 12)
        x += 255
        if x >= 500:
            x = 40
            y += -310
        if y <= 50:
            c.showPage()
            x = 40
            y = 500
    c.save();
    return send_from_directory(directory=directory, filename=file_name)