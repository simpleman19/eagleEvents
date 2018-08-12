from . import db
import uuid
from sqlalchemy import event
from sqlalchemy_utils import UUIDType


class Customer(db.Model):
    __tablename__ = 'customer'
    id = db.Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    number = db.Column(db.Integer)
    name = db.Column(db.String(200))
    phone_number = db.Column(db.String(26))
    email = db.Column(db.String(150))
    events = db.relationship('Event', lazy=True, cascade='all,delete')
    company_id = db.Column(UUIDType(binary=False), db.ForeignKey('company.id'))
    company = db.relationship('Company', lazy=False)

    def __init__(self, company: 'Company'):
        self.company = company


# This auto generates customer numbers on insert
@event.listens_for(Customer, 'after_insert')
def gen_customer_number(mapper, connection, target):
    connection.execute(
        "Update customer set number = (select IFNULL(max(number), 1000) + 1 from customer) where id is '" +
        str(target.id.hex) + "'")
