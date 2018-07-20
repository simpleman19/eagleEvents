from eagleEvents.models import db
from sqlalchemy_utils import UUIDType
import uuid


class Company(db.Model):
    __tablename__ = 'company'
    id = db.Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(250), nullable=False)
    # table_sizes = db.relationship()
    # users = db.relationship()
    customers = db.relationship('Customer', lazy=True,
                                backref=db.backref('customer', lazy='subquery'))
    # events = db.relationship()
