from . import db
import uuid
import bcrypt
from sqlalchemy_utils import UUIDType
from typing import List


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(120), nullable=False)
    username = db.Column(db.String(40), nullable=False)
    password = db.Column(db.LargeBinary(100), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    company_id = db.Column(UUIDType(binary=False), db.ForeignKey('company.id'))
    company: 'Company' = db.relationship('Company', lazy=False)
    events: List['Event'] = db.relationship('Event', lazy=True)

    def __init__(self, company: 'Company'):
        self.company = company

    # Implemented very simple password hashing and checking (copied from another project)
    def verify_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password)

    def set_password(self, new_password, old_password=""):
        if self.password is None or self.password == "":
            self.password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
            return True
        elif bcrypt.checkpw(old_password.encode('utf-8'), self.password):
            self.password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
            return False
