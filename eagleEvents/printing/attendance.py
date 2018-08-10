import sys
import os
import datetime
from flask import send_from_directory
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from eagleEvents.models import Event, Guest
from eagleEvents import db



def attendance_list_print(id_event):
    e = Event.query.filter(Event.id == id_event)[0]
    guests = Guest.query.filter(Guest.event_id == id_event).order_by(Guest.last_name)
    current_directory = os.getcwd();
    final_directory = os.path.join(current_directory, 'temp')
    if not os.path.exists(final_directory):
        os.makedirs(final_directory);

    file_name = 'attendanceList.pdf'

    doc = SimpleDocTemplate(os.path.join(final_directory , file_name), pagesize=letter)
    doc.title = e.name + "-attendance-" + str(e.time.date()) + ".pdf"

    story = []
    elements = []
    outer_data = []
    inner_data = []

    # text styles
    sample_styles = getSampleStyleSheet()
    style = sample_styles['Normal']
    style.fontSize = 16
    style.leading = 20
    style_header1 = sample_styles['Heading2']
    style_header1.fontSize = 11
    style_header1.leading = 10
    style_header1.alignment = TA_LEFT
    style_header2 = sample_styles['Heading1']
    style_header2.fontSize = 16
    style_header2.leading = 20
    style_header2.alignment = TA_CENTER

    # header
    header1 = Paragraph('Eagle Events', style_header1)
    story.append(header1)
    header1 = Paragraph(e.name, style_header1)
    story.append(header1)
    year, month, day = str(e.time.date()).split("-")
    hour, min, second = str(e.time.time()).split(":")
    header1 = Paragraph("Event Date: " + month + "/" + day + "/" + year, style_header1)
    story.append(header1)
    header1 = Paragraph("Event Time: " +  hour + ":" + min, style_header1)
    story.append(header1)
    header2 = Paragraph("Attendance List", style_header2)
    story.append(header2)


    text_wrap = Paragraph("Table Number", style)
    inner_data = [Paragraph('Last Name', style), Paragraph('First Name', style), Paragraph('Title', style), Paragraph('Table Number', style)]
    outer_data.append(inner_data)
    style.fontSize = 14
    for g in guests:
        inner_data = [Paragraph(g.last_name, style), Paragraph(g.first_name, style), Paragraph(g.title, style),Paragraph(str(g.assigned_table.number), style)]
        outer_data.append(inner_data)


    t=Table(outer_data, repeatRows=1)

    # black border
    t.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 0.25, colors.black),
                       ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black)]))
    # grey header
    t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey)]))


 
    story.append(t)

    doc.build(story)

    return send_from_directory(directory=final_directory, filename=file_name)