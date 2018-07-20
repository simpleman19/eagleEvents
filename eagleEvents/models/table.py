from . import db
import uuid
from sqlalchemy import event
from sqlalchemy_utils import UUIDType


class Table(db.Model):
    __tablename__ = 'event_table'
    id = db.Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    number = db.Column(db.Integer)
    seating_capacity = db.Column(db.Integer)
    event_id = db.Column(UUIDType(binary=False), db.ForeignKey('event.id'))
    event = db.relationship('Event', lazy=False)
    guests = db.relationship('Guest', lazy=True,
                             backref=db.backref('guest', lazy='subquery'))

    def __init__(self, event):
        self.event = event


# This auto generates customer numbers on insert
@event.listens_for(Table, 'after_insert')
def gen_customer_number(mapper, connection, target):
    connection.execute(
        "Update event_table set number = (select IFNULL(max(number), 0) + 1 from event_table where event_id is '" +
        str(target.event_id.hex) + "') where id is '" + str(target.id.hex) + "'")