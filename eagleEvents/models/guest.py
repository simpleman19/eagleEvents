from . import db
import uuid
import enum
from sqlalchemy_utils import UUIDType
from typing import List


class SeatingPreference(enum.Enum):
    DISLIKE = 0
    LIKE = 1


class SeatingPreferenceTable(db.Model):
    __tablename__ = 'seating_preference'
    id = db.Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    guest_id = db.Column(UUIDType(binary=False), db.ForeignKey('guest.id'))
    guest: 'Guest' = db.relationship('Guest', lazy=True, foreign_keys=[guest_id], back_populates='seating_preferences')
    other_guest_id = db.Column(UUIDType(binary=False), db.ForeignKey('guest.id'))
    other_guest: 'Guest' = db.relationship('Guest', lazy=True, foreign_keys=[other_guest_id])
    preference: SeatingPreference = db.Column(db.Enum(SeatingPreference), nullable=False)

    def __init__(self, guest: 'Guest', other_guest: 'Guest', preference: 'SeatingPreference'):
        self.guest = guest
        self.other_guest = other_guest
        self.preference = preference


class Guest(db.Model):
    __tablename__ = 'guest'
    id = db.Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    number = db.Column(db.Integer, nullable=False, index=True)
    last_name = db.Column(db.String(50), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    event_id = db.Column(UUIDType(binary=False), db.ForeignKey('event.id'), index=True)
    event: 'Event' = db.relationship('Event', lazy=True)
    table_id = db.Column(UUIDType(binary=False), db.ForeignKey('event_table.id'))
    assigned_table: 'Table' = db.relationship('Table', lazy=True)
    seating_preferences: List[SeatingPreferenceTable] = db.relationship('SeatingPreferenceTable', lazy=False,
                                                                        back_populates='guest', foreign_keys=[SeatingPreferenceTable.guest_id],
                                                                        cascade='all,delete')

    def __init__(self, event):
        self.event = event

    def __str__(self):
        return 'guest: {}, number: {}'.format(self.id, self.number)

    @property
    def full_name(self):
        return '{}, {}'.format(self.last_name, self.first_name)

    # TODO stubbed but not fully tested
    def likes(self, guest: 'Guest') -> bool:
        if self.seating_preferences is not None and len(self.seating_preferences) > 0:
            for p in self.seating_preferences:
                if p.preference == SeatingPreference.LIKE and p.other_guest_id == guest.id:
                    return True
        return False

    # TODO stubbed but not fully tested
    def dislikes(self, guest: 'Guest') -> bool:
        if self.seating_preferences is not None and len(self.seating_preferences) > 0:
            for p in self.seating_preferences:
                if p.preference == SeatingPreference.DISLIKE and p.other_guest_id == guest.id:
                    return True
        return False
