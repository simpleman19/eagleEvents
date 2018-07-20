from . import db
from eagleEvents.models import User
from sqlalchemy_utils import UUIDType
import uuid
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


class TableSize(db.Model):
    __tablename__ = 'table_sizes'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    company_id = db.Column(UUIDType(binary=False), db.ForeignKey('company.id'))
    size = db.Column(db.Integer, nullable=False)

    def __init__(self, company_id, size):
        self.company_id = company_id
        self.size = size
