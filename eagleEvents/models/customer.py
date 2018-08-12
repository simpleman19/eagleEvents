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

    """
    Returns a list of error messages
    If validation is successful, it saves the customer and returns an empty list
    """
    @staticmethod
    def validate_and_save(customer, customer_data):
        errors = []
        if 'name' in customer_data:
            customer.name = customer_data['name']
        if 'email' in customer_data:
            customer.email = customer_data['email']
        if 'phone' in customer_data:
            customer.phone_number = customer_data['phone']
        if customer.name is None or len(customer.name) == 0:
            errors.append("Name is required")
        else:
            db.session.add(customer)
            db.session.commit()
        return errors


# This auto generates customer numbers on insert
@event.listens_for(Customer, 'after_insert')
def gen_customer_number(mapper, connection, target):
    connection.execute(
        "Update customer set number = (select IFNULL(max(number), 1000) + 1 from customer) where id is '" +
        str(target.id.hex) + "'")
