from flask import flash

from eagleEvents.seating_chart_ga import SeatingChartGA
from . import db
from eagleEvents.models import Guest, User, Customer, TableSize
import uuid, datetime
from eagleEvents.models import Guest
from sqlalchemy_utils import UUIDType
from typing import List


class Event(db.Model):
    __tablename__ = 'event'
    id = db.Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    time = db.Column(db.DateTime, nullable=False)
    is_done = db.Column(db.Boolean, nullable=False, default=False)
    venue = db.Column(db.String(150), nullable=False, default="")
    name = db.Column(db.String(150), nullable=False, default="")
    percent_extra_seats = db.Column(db.Float, nullable=False, default=10)
    customer_id = db.Column(UUIDType(binary=False), db.ForeignKey('customer.id'))
    customer = db.relationship('Customer', lazy=False)
    company_id = db.Column(UUIDType(binary=False), db.ForeignKey('company.id'))
    company = db.relationship('Company', lazy=False)
    planner_id = db.Column(UUIDType(binary=False), db.ForeignKey('users.id'), nullable=True)
    planner = db.relationship('User', lazy=False)
    tables = db.relationship('Table', lazy=False, cascade='delete')
    table_size_id = db.Column(db.Integer, db.ForeignKey('table_sizes.id'), nullable=True)
    table_size = db.relationship('TableSize', lazy=False)
    _guests: List[Guest] = db.relationship('Guest', lazy=True,
                    backref=db.backref('guests', lazy='subquery'), cascade='delete')

    def __init__(self, customer):
        self.customer = customer
        self.company = customer.company

    def set_guests(self, guests: List['Event']):
        _guests = guests
        self.generate_seating_chart()

    def generate_seating_chart(self):
        # delete old tables
        for t in self.tables:
            db.session.delete(t)
        db.session.commit()

        new_tables = SeatingChartGA(self).get_seating_chart_tables()

        # add new tables
        for t in new_tables:
            db.session.add(t)
        self.tables = new_tables
        db.session.commit()

    @staticmethod
    def validate_and_save(event, request):
        if float(request.form['extra']) > .99:
            flash("Percent value must be less than 1", "error")
            return False
        regen_seating_chart = False
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
        new_table_size = TableSize.query.filter_by(id=request.form['table_size']).one_or_none()
        if new_table_size.id != event.table_size_id:
            regen_seating_chart = True
        event.table_size = new_table_size
        if event.percent_extra_seats != request.form['extra']:
            regen_seating_chart = True
        event.percent_extra_seats = float(request.form['extra'])

        if event.name is None or len(event.name) == 0:
            flash("Name is required", "error")
            return False
        elif event.venue is None or len(event.venue) == 0:
            flash("Venue is required", "error")
            return False
        elif event.time is None or event.time < datetime.datetime.now():
            flash("Valid Date and Time is required", "error")
            return False
        elif event.percent_extra_seats is None:
            flash("Extra Seating Percentage is required", "error")
            return False

        if regen_seating_chart and len(event._guests) > 0:
            event.generate_seating_chart()

        db.session.add(event)
        db.session.commit()
        return True
