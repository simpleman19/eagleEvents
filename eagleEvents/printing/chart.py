import sys
import os
import datetime
from flask import send_from_directory
from reportlab.pdfgen import canvas
from eagleEvents.models import Event, Table, Guest
from eagleEvents import db



def seating_chart_print(id_event):
    e = Event.query.filter(Event.id == id_event)[0]
    tables = Table.query.filter(Table.event_id == id_event)
    guests = Guest.query.filter(Guest.event_id == id_event)
    current_directory = os.getcwd();
    final_directory = os.path.join(current_directory, 'temp')
    if not os.path.exists(final_directory):
        os.makedirs(final_directory);

    file_name = 'seatingChart.pdf'

    c = canvas.Canvas(os.path.join(final_directory , file_name))
    c.setTitle(str(e.name) + "-" + str(e.time.date()) + ".pdf")

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
    small_table_factor = 150
    for t in tables:
        guests_for_table = guests.filter(Guest.table_id == t.id)
        guests_for_table = guests_for_table.order_by(Guest.last_name)
        if t.seating_capacity <= 5:
            c.roundRect(x, y + small_table_factor, 250, 150, 4, stroke=1, fill=0)
            shift_x = 10
            shift_y = 135
        else:
            small_table_factor = 0;
            c.roundRect(x, y + small_table_factor, 250, 300, 4, stroke=1, fill=0)
            shift_x = 10
            shift_y = 275
        c.setFont("Helvetica-Bold", 12)
        c.drawString(x + shift_x, y + shift_y + small_table_factor, "Table " + str(t.number))
        shift_y += -20
        c.drawString(x + shift_x, y + shift_y + small_table_factor, "Last Name  ")
        c.drawString(x + shift_x + 90, y + shift_y + small_table_factor, "First Name  ")
        c.drawString(x + shift_x + 180, y + shift_y + small_table_factor, "Title")
        shift_y += -20
        c.setFont("Helvetica", 10)
        for guest in guests_for_table:
            last_name_to_print = guest.last_name
            if(len(last_name_to_print) > 11):
                last_name_to_print = last_name_to_print[:11] + "..."
            c.drawString(x + shift_x, y + shift_y + small_table_factor, last_name_to_print)


            first_name_to_print = guest.first_name
            if(len(first_name_to_print) > 10):
                first_name_to_print = first_name_to_print[:10] + "..."
            c.drawString(x + shift_x + 90, y + shift_y + small_table_factor, first_name_to_print)

            title_to_print = guest.title
            if(len(title_to_print) > 10):
                title_to_print = title_to_print[:8] + "..."
            c.drawString(x + shift_x + 180, y + shift_y + small_table_factor, title_to_print)

            shift_y += -20
        c.setFont("Helvetica", 12)
        x += 255
        if x >= 500:
            x = 40
            y += -310
            if small_table_factor != 0: 
                small_table_factor += 150;
        if y <= 50 and small_table_factor == 0 or y <= -300 and small_table_factor != 0:
            c.showPage()
            x = 40
            y = 500
            if small_table_factor != 0: 
                small_table_factor = 150;
    c.save();
    return send_from_directory(directory=final_directory, filename=file_name)