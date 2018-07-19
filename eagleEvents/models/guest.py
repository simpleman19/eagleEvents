from . import db
import uuid


class Guest(db.Model):
    __tablename__ = 'guest'
    id = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()))
    number = db.Column(db.Integer, nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    # event_id = db.Column()
    # assigned_table = db.Column()
    # seating_preference = db.Column()
