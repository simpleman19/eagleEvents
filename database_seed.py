from eagleEvents.models import Company, Customer, Event, Table, Guest, SeatingPreferenceTable, SeatingPreference, User
from eagleEvents import db
import datetime


# TODO Actually seed, this was just to ensure database works
def seed_db():
    company = Company()
    company.name = "Test company"
    company.table_sizes = [2, 4, 6]
    db.session.add(company)
    db.session.commit()
    user = User(company)
    user.username = 'test'
    user.name = 'A User'
    user.set_password('password')
    db.session.add(user)
    db.session.commit()

    for x in range(10):
        customer = Customer(company)
        customer.name = "Test customer"
        customer.phone_number = "+1 (800) 123-4567 ext. 1234"
        customer.email = "test@customer.com"
        db.session.add(customer)
        db.session.commit()
        event = Event(customer)
        event.name = "Test Event"
        event.venue = "Test Venue"
        event.percent_extra_seats = .2
        event.time = datetime.datetime.now()
        db.session.add(event)
        db.session.commit()

        for i in range(10):
            table = Table(event)
            db.session.add(table)
            for k in range(4):
                guest = Guest(event)
                guest.assigned_table = table
                guest.first_name = "First"
                guest.last_name = "Last"
                guest.number = k + i * 4
                guest.title = "A Title"
                db.session.add(guest)
            guests = Guest.query.all()
            seating_preference = SeatingPreferenceTable(guests[0], guests[1], SeatingPreference.LIKE)
            db.session.add(seating_preference)
            seating_preference = SeatingPreferenceTable(guests[1], guests[2], SeatingPreference.DISLIKE)
            db.session.add(seating_preference)
        db.session.commit()
