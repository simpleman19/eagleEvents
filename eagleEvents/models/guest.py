from . import db
import uuid
import enum
from sqlalchemy_utils import UUIDType


class SeatingPreference(enum.Enum):
    DISLIKE = 0
    LIKE = 1


class SeatingPreferenceTable(db.Model):
    __tablename__ = 'seating_preference'
    id = db.Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    guest_id = db.Column(UUIDType(binary=False), db.ForeignKey('guest.id'))
    guest = db.relationship('Guest', lazy=True, foreign_keys=[guest_id], back_populates='seating_preferences')
    other_guest_id = db.Column(UUIDType(binary=False), db.ForeignKey('guest.id'))
    other_guest = db.relationship('Guest', lazy=True, foreign_keys=[other_guest_id])
    preference = db.Column(db.Enum(SeatingPreference), nullable=False)

    def __init__(self):
        return

    def __init__(self, guest, other_guest, preference):
        self.guest = guest
        self.other_guest = other_guest
        self.preference = preference


class Guest(db.Model):
    __tablename__ = 'guest'
    id = db.Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    number = db.Column(db.Integer, nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    event_id = db.Column(UUIDType(binary=False), db.ForeignKey('event.id'))
    event = db.relationship('Event', lazy=True)
    table_id = db.Column(UUIDType(binary=False), db.ForeignKey('event_table.id'))
    assigned_table = db.relationship('Table', lazy=True)
    seating_preferences = db.relationship('SeatingPreferenceTable', lazy=False,
                                          back_populates='guest', foreign_keys=[SeatingPreferenceTable.guest_id])

    def __init__(self, event):
        self.event = event

