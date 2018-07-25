from . import db
import uuid
from sqlalchemy_utils import UUIDType
from typing import List


class Event(db.Model):
    __tablename__ = 'event'
    id = db.Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    time = db.Column(db.DateTime, nullable=False)
    is_done = db.Column(db.Boolean, nullable=False, default=False)
    venue = db.Column(db.String(150), nullable=False, default="")
    name = db.Column(db.String(150), nullable=False, default="")
    percent_extra_seats = db.Column(db.Float, nullable=False)
    customer_id = db.Column(UUIDType(binary=False), db.ForeignKey('customer.id'))
    customer = db.relationship('Customer', lazy=False)
    company_id = db.Column(UUIDType(binary=False), db.ForeignKey('company.id'))
    company = db.relationship('Company', lazy=False)
    planner_id = db.Column(UUIDType(binary=False), db.ForeignKey('users.id'), nullable=True)
    planner = db.relationship('User', lazy=False)
    tables = db.relationship('Table', lazy=False)

    def __init__(self, customer):
        self.customer = customer

    def set_guests(self, guests: List['Event']):
        pass

    def generate_seating_chart(self):
        pass

    def _generate_genetic_algo(self):
        pass
