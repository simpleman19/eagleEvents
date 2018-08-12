import sys
import os
import datetime
from flask import send_from_directory
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, TableStyle, Paragraph, PageBreak
from reportlab.platypus import Table as pdfTable
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from eagleEvents.models import Event, Guest, Table
from eagleEvents import db



def table_card_print(id_event):
    e = Event.query.filter(Event.id == id_event)[0]
    guests = Guest.query.filter(Guest.event_id == id_event)
    tables = Table.query.filter(Table.event_id == id_event)
    current_directory = os.getcwd();
    final_directory = os.path.join(current_directory, 'temp')
    if not os.path.exists(final_directory):
        os.makedirs(final_directory);

    file_name = 'tableCard.pdf'

    doc = SimpleDocTemplate(os.path.join(final_directory , file_name), pagesize=letter)
    doc.title = e.name + "-cards-" + str(e.time.date()) + ".pdf"

    story = []
    elements = []
    outer_data = []
    inner_data = []

    # text styles
    sample_styles = getSampleStyleSheet()
    style = sample_styles['Normal']
    style.fontSize = 12
    style.leading = 20
    style_header1 = sample_styles['Heading2']
    style_header1.fontSize = 14
    style_header1.leading = 10
    style_header1.alignment = TA_CENTER
    style_header2 = sample_styles['Heading1']
    style_header2.fontSize = 16
    style_header2.leading = 20
    style_header2.alignment = TA_CENTER

    for t in tables:
        # header
        header1 = Paragraph('Welcome To:', style_header1)
        story.append(header1)
        header2 = Paragraph(e.name, style_header2)
        story.append(header2)
        header1 = Paragraph('Table ' + str(t.number), style_header1)
        story.append(header1)

        # table
        inner_data = [Paragraph('First Name', style), Paragraph('Last Name', style), Paragraph('Title', style)]
        outer_data.append(inner_data)
        style.fontSize = 10
        guests_for_table = guests.filter(Guest.table_id == t.id)
        guests_for_table = guests_for_table.order_by(Guest.last_name)
        for g in guests_for_table:
            inner_data = [Paragraph(g.first_name, style), Paragraph(g.last_name, style), Paragraph(g.title, style)]
            outer_data.append(inner_data)

        t=pdfTable(outer_data)
        outer_data = []
        style.fontSize = 12

        # black border
        t.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 0.25, colors.black),
                        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black)]))
        # grey header
        t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey)]))

        story.append(t)
        story.append(PageBreak())

    doc.build(story)

    return send_from_directory(directory=final_directory, filename=file_name)