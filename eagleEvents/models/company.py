from . import db
import uuid


class Company(db.Model):
    __tablename__ = 'company'
    id = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()))
    name = db.Column(db.String(250), nullable=False)
    # table_sizes = db.relationship()
    # users = db.relationship()
    # customers = db.relationship()
    # events = db.relationship()
