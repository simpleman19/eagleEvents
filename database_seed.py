from eagleEvents.models import Company, Customer, Event, Table, Guest, SeatingPreferenceTable, SeatingPreference, User
from eagleEvents import db
import datetime
from random import randint
import random
random.seed()

'''
Private helper functions for the main seed function. 
'''

def __get_company_name(i: int):
    """
    used to get name for each of our 10 test customers
        :param i:int: which company to get
    """
    if i == 0:
        return "Disney"
    elif i == 1:
        return "IHop"
    elif i == 2:
        return "IHob"
    elif i == 3:
        return "Staples"
    elif i == 4:
        return "Krispy Kreme"
    elif i == 5:
        return "PetCo"
    elif i == 6:
        return "Starbucks"
    elif i == 7:
        return "O'Reilly Auto Parts"
    elif i == 8:
        return "Studio Ghibli"
    else:
        return "Full Circle Books"
    

def __get_person_name(first):
    """
    used to get customer names and guest names 
        :param first: true for first names and false for last names
    """
    names_first = ["Ruth", "Becca", "Sam", "Chad", "Bryson", "Chris", "Jacob", "Katie", "Zac", "Dani", "Jen",
    "Trey", "Hannah", "James", "Carly", "Logan", "Peter", "Brandon", "Macy", "Melody", "Lance", "Nancy", "Ryan",
    "Nathan", "Pierce", "Connie", "Morgan", "Jon", "Ashley", "Kara", "Matt", "Whitney", "Seth", "Kelsey", "Justin", 
    "Matthew", "Celeste", "Holly", "Cheyenne", "Tom", "Kennedy", "Jordan", "Artie", "Jules", "Kevin", "Mike", "Mark",
    "Logan", "Cody", "Bella", "Jacob", "Emmett", "Alice", "Jasper", "Esme", "Rose", "Ben", "Harry", "Ron", "George", 
    "Fred", "Ginny", "Draco", "Tonks", "Luke", "Anakin", "Daphne", "Velma", "Shaggy", "Robin", "Sara", "Rachel", "Dom", 
    "Caleb", "Olivia", "Sydney", "Madison", "Victoria", "Emily", "Paris", "Brett", "Courtney", "Megan", "Reed", "Kim", 
    "Cynthia", "Blaine", "Kurt", "Finn", "Puck", "Quinn", "Santana", "Brittany", "Will", "Sue", "Mercedes", "Sebastian",
    "Shannon", "Jessie", "Dave", "Emma", "Tina", "Ryder", "Sugar", "Joe", "Rory", "Hunter", "Shelby", "Cassandra", "Roderick",
    "Elliot", "Myron", "Terri", "Mason", "Spencer", "Burt", "Roz", "Carole", "Marley", "Jane", "Becky", "Liz"]
    names_last = ["Berry", "Anderson", "Hummel", "Hudson", "Fabray", "Lopez", "Abrams", "Pierce", "Schuester", "Evans",
    "Sylvester", "Jones", "Chang", "Smythe", "Beiste", "St. James", "Karofsky", "Pillsbury", "Wilde", "Choen-Chang", 
    "Holliday", "Lynn", "Motta", "Hart", "Flanagan", "Clarington", "Zizes", "Corcoran", "Puckerman", "July", "Meeks",
    "Gilbert", "Muskoitz", "Figgins", "McCarthy", "Porter", "Rutherford", "Washington", "Hayward", "Rose", "Jackson",
    "DiLaurentis", "Montgomery", "Hastings", "Marin", "Fields", "Drake", "Vanderwaal", "Fitz", "Marshall", "Cavanaugh", "Rivers",
    "Kahn", "St. Germain", "Kingston", "Wilden", "Thomas", "McCullers", "Santiago", "Gottesman", "Holt", "Reynolds", 
    "Sullivan", "Ackard", "Sorenson", "Driscoll", "Randall", "Kerr", "Molina", "Tanner", "Fitzgerald", "Coogan", "Maple",
    "Vasquez", "Kennish", "Sorrento", "Wilkerson", "Mendosa", "Redford", "Salvatore", "Mikaelson", "Forbes", "Bennet",
    "Saltzman", "Parker", "Lockwood", "Donovan", "Sommers", "Young", "Maxfield", "Cooke", "Dowling", "Wilson", "Branson"]
    
    if first:
        rand = randint(0, len(names_first)-1)
        return names_first[rand]
    else:
        rand = randint(0, len(names_last)-1)
        return names_last[rand]  


def __get_table_num():
    """
    used to get a random table size to use
    """
    rand = randint(0, 4)

    if rand == 0:
        return 4
    elif rand == 1:
        return 6
    elif rand == 2:
        return 8
    else:
        return 12


def __get_title():
    """
    used to get a random title or not a title
    """
    rand = randint(0, 4)

    if rand == 0:
        return "CEO"
    elif rand == 1:
        return "President"
    elif rand == 2:
        return ""
    else:
        return ""


def __get_phone_number():
    """
    used to get a random phone number
    """
    rand1 = randint(0, 9)
    rand2 = randint(0, 9)
    rand3 = randint(0, 9)
    rand4 = randint(0, 9)
    rand5 = randint(0, 9)
    rand6 = randint(0, 9)
    rand7 = randint(0, 9)

    return "+1 (800) " + str(rand1) + str(rand2) + str(rand3) + "-" + str(rand4) + str(rand5) + str(rand6) + str(rand7)


def __get_date():
    """
    used to get a random date & see if it is passed or not
    """
    datetime_info = {}
    rand = randint(0,4)
    year: int
    if rand == 0:
        year = 2016
    elif rand == 1:
        year = 2017
    elif rand == 2:
        year = 2018
    elif rand == 3:
        year = 2019
    else:
        year = 2020

    try:
        date_event = datetime.datetime.strptime('{} {}'.format(random.randint(1, 366), year), '%j %Y')
        now = datetime.datetime.now()
        if date_event < now:
            done = True
        else:
            done = False
        datetime_info["date"] = date_event
        datetime_info["done_status"] = done
        return datetime_info

    except ValueError:
        get_date()


def seed_db():
    """
    Used to seed the database
    """
    company = Company()
    company.name = "Eagle Events"
    company.table_sizes = [2, 4, 6, 12]
    db.session.add(company)
    db.session.commit()
    want_a_bunch_of_stuff = input("Want a bunch of stuff? y - Yes or n - No :")
    if want_a_bunch_of_stuff == "y":
        # Users created (Emily, Jacob, Dee Dee, Paresa, Chance)
        user = User(company)
        user.username = 'ePielemeier'
        user.name = 'Emily Pielemier'
        user.set_password('password0')
        user.is_admin = True
        user.is_active = True
        db.session.add(user)
        db.session.commit()
        user = User(company)
        user.username = 'jCollins'
        user.name = 'Jacob Collins'
        user.set_password('password1')
        user.is_admin = True
        user.is_active = True
        db.session.add(user)
        db.session.commit()
        user = User(company)
        user.username = 'dMcCroskey'
        user.name = 'Dee Dee McCroskey'
        user.set_password('password2')
        user.is_admin = True
        user.is_active = True
        db.session.add(user)
        db.session.commit()
        user = User(company)
        user.username = 'pNoorossana'
        user.name = 'Paresa Noorossana'
        user.set_password('password3')
        user.is_admin = True
        user.is_active = True
        db.session.add(user)
        db.session.commit()
        user = User(company)
        user.username = 'cTurner'
        user.name = 'Chance Turner'
        user.set_password('password4')
        user.is_admin = True
        user.is_active = True
        db.session.add(user)
        db.session.commit()
        user = User(company)
        user.username = 'planner'
        user.name = 'Planner'
        user.set_password('password')
        user.is_admin = False
        user.is_active = True
        db.session.add(user)
        db.session.commit()
        user.username = 'admin'
        user.name = 'Admin'
        user.set_password('password')
        user.is_admin = True
        user.is_active = True
        db.session.add(user)
        db.session.commit()
        user = User(company)
        user.username = 'tSwift'
        user.name = 'Taylor Swift'
        user.set_password('password5')
        user.is_admin = False
        user.is_active = False
        db.session.add(user)
        db.session.commit()

        # create customers 
        for x in range(10):
            customer = Customer(company)
            customer.name = __get_company_name(x)
            customer.phone_number = __get_phone_number()
            customer.email = "ceo@" + __get_company_name(x) + ".com"
            db.session.add(customer)
            db.session.commit()

            # create events for customers
            for y in range(3):
                event = Event(customer)
                event.name = __get_company_name(x) + "'s Awesome Event " + str(y)
                event.venue = __get_company_name(x) + "'s Venue"
                event.percent_extra_seats = random.uniform(0.1,0.3)
                info_date = __get_date()
                event.time = info_date["date"]
                event.is_done = info_date["done_status"]
                db.session.add(event)
                db.session.commit()
                tables_to_have = randint(10,25)

                # create tables for events
                guests_status = randint(1,4)
                for i in range(tables_to_have):
                    table = Table(event)
                    db.session.add(table)
                    table_num = __get_table_num()

                    # create guests for tables
                    if guests_status != 2:
                        for k in range(table_num):
                            rand = randint(1,10)
                            if rand != 1:
                                guest = Guest(event)
                                guest.assigned_table = table
                                guest.first_name = __get_person_name(True)
                                guest.last_name = __get_person_name(False)
                                guest.number = k + i * table_num
                                guest.title = __get_title()
                                db.session.add(guest)
                        guests = Guest.query.all()
                        try:
                            seating_preference = SeatingPreferenceTable(guests[0], guests[int(table_num/2)], SeatingPreference.LIKE)
                            db.session.add(seating_preference)
                            seating_preference = SeatingPreferenceTable(guests[1], guests[3], SeatingPreference.DISLIKE)
                            db.session.add(seating_preference)
                        except Exception:
                            seating_preference = SeatingPreferenceTable(guests[0], guests[1], SeatingPreference.DISLIKE)
                            db.session.add(seating_preference)

            db.session.commit()
    else:
        # Users created (planner & admin)
        user = User(company)
        user.username = 'planner'
        user.name = 'Planner'
        user.set_password('password')
        user.is_admin = False
        user.is_active = True
        db.session.add(user)
        db.session.commit()
        user.username = 'admin'
        user.name = 'Admin'
        user.set_password('password')
        user.is_admin = True
        user.is_active = True
        db.session.add(user)
        db.session.commit()
        user.username = 'fired planner'
        user.name = 'Fired Planner'
        user.set_password('password')
        user.is_admin = False
        user.is_active = False
        db.session.add(user)
        db.session.commit()

        # create customers 
        for x in range(5):
            customer = Customer(company)
            customer.name = __get_company_name(x)
            customer.phone_number = __get_phone_number()
            customer.email = "ceo@" + __get_company_name(x) + ".com"
            db.session.add(customer)
            db.session.commit()

            # create events for customers
            for y in range(2):
                event = Event(customer)
                event.name = __get_company_name(x) + "'s Awesome Event " + str(y)
                event.venue = __get_company_name(x) + "'s Venue"
                event.percent_extra_seats = random.uniform(0.1,0.3)
                info_date = __get_date()
                event.time = info_date["date"]
                event.is_done = info_date["done_status"]
                db.session.add(event)
                db.session.commit()
                tables_to_have = randint(10,20)

                # create tables for events
                guests_status = randint(1,4)
                for i in range(tables_to_have):
                    table = Table(event)
                    db.session.add(table)
                    table_num = __get_table_num()
                    
                    # create guests for tables
                    if guests_status !=2:
                        for k in range(table_num):
                            rand = randint(1,10)
                            if rand != 1:
                                guest = Guest(event)
                                guest.assigned_table = table
                                guest.first_name = __get_person_name(True)
                                guest.last_name = __get_person_name(False)
                                guest.number = k + i * table_num
                                guest.title = __get_title()
                                db.session.add(guest)
                        guests = Guest.query.all()
                        try:
                            seating_preference = SeatingPreferenceTable(guests[0], guests[int(table_num/2)], SeatingPreference.LIKE)
                            db.session.add(seating_preference)
                            seating_preference = SeatingPreferenceTable(guests[1], guests[3], SeatingPreference.DISLIKE)
                            db.session.add(seating_preference)
                        except Exception:
                            seating_preference = SeatingPreferenceTable(guests[0], guests[1], SeatingPreference.DISLIKE)
                            db.session.add(seating_preference)

            db.session.commit()
        

    