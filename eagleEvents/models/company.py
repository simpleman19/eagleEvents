from . import db
from eagleEvents.models import User
from eagleEvents.models.guest import *
from sqlalchemy_utils import UUIDType
import uuid
import csv
from typing import List


class Company(db.Model):
    __tablename__ = 'company'
    id = db.Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(250), nullable=False)
    users = db.relationship('User', lazy=True)
    _table_sizes = db.relationship('TableSize', lazy=False)
    customers = db.relationship('Customer', lazy=True,
                                backref=db.backref('customer', lazy='subquery'))
    events = db.relationship('Event', lazy=True)

    # This is a little abstraction to make sizes easier to deal with but still mapped with the ORM
    @property
    def table_sizes(self) -> List[int]:
        return [ts.size for ts in self._table_sizes]

    @table_sizes.setter
    def table_sizes(self, values: List[int]):
        self._table_sizes = [TableSize(self.id, v) for v in values]

    def get_event_planners(self) -> List[User]:
        return self.users

    def import_guest_list(self, file_name):
        with open(file_name) as csv_file:
            read_csv = csv.reader(csv_file, delimiter=',')

            header = next(read_csv)
            dislikes = header.count("different_table")

            for row in read_csv:
                g = Guest(None)
                g.id = uuid.uuid4()
                g.number = row[0]
                g.title = row[1]
                g.first_name = row[2]
                g.last_name = row[3]

                for i in range(4, len(header) - dislikes, 1):
                    if row[i] is not None:
                        pref = SeatingPreferenceTable(g, g, SeatingPreference.LIKE)
                        g.seating_preferences.append(pref)
                        print('Likes ', row[i])

                for j in range(len(header) - dislikes, len(header), 1):
                    if row[j] is not None:
                        pref = SeatingPreferenceTable(g, g, SeatingPreference.DISLIKE)
                        g.seating_preferences.append(pref)
                        print('Dislikes ', row[j])


class TableSize(db.Model):
    __tablename__ = 'table_sizes'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    company_id = db.Column(UUIDType(binary=False), db.ForeignKey('company.id'))
    size = db.Column(db.Integer, nullable=False)

    def __init__(self, company_id, size):
        self.company_id = company_id
        self.size = size
