from eagleEvents.models import Company
from eagleEvents import db


def seed_db():
    company = Company()
    company.name = "Test company"
    db.session.add(company)
    db.session.commit()