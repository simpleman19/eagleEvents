from . import db
import uuid
from sqlalchemy import event
from sqlalchemy_utils import UUIDType
from typing import List


class Table(db.Model):
    __tablename__ = 'event_table' # Turns out table is a sqlite keyword..
    id = db.Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    # Auto generated
    number: int = db.Column(db.Integer)
    seating_capacity: int = db.Column(db.Integer)
    event_id = db.Column(UUIDType(binary=False), db.ForeignKey('event.id'))
    event: 'Event' = db.relationship('Event', lazy=False)
    guests: List['Guest'] = db.relationship('Guest', lazy=True,
                                            backref=db.backref('guest', lazy='subquery'))

    def __init__(self, event: 'Event'):
        self.event = event

    def num_open_seats(self) -> int:
        # Assumed guests is never None, change if causes problems later
        return self.seating_capacity - len(self.guests)

    def num_guests_likes(self, guest: 'Guest') -> int:
        likes = 0
        for g in self.guests:
            if g.likes(guest):
                likes += 1
        return likes

    def num_guests_dislikes(self, guest: 'Guest') -> int:
        dislikes = 0
        for g in self.guests:
            if g.dislikes(guest):
                dislikes += 1
        return dislikes


# This auto generates table numbers on insert
@event.listens_for(Table, 'after_insert')
def gen_customer_number(mapper, connection, target):
    connection.execute(
        "Update event_table set number = (select IFNULL(max(number), 0) + 1 from event_table where event_id is '" +
        str(target.event_id.hex) + "') where id is '" + str(target.id.hex) + "'")