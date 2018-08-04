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
    customers = ["Disney", "IHop", "IHob", "Staples",
    "Krispy Kreme", "PetCo", "Starbucks", "O'Reilly Auto Parts", 
    "Studio Ghibli", "Full Circle Books"];
    return customers[i];
    

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
    rand = randint(0, 3)
    table_sizes = [4, 6, 8, 12];
    return table_sizes[rand]


def __get_title():
    """
    used to get a random title or not a title
    """
    rand = randint(0, 3)
    rand_titles = ["CEO", "President", "", ""];
    return rand_titles[rand]


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
        user0 = User(company)
        user0.username = 'ePielemeier'
        user0.name = 'Emily Pielemier'
        user0.set_password('password0')
        user0.is_admin = True
        user0.is_active = True
        db.session.add(user0)
        db.session.commit()
        user1 = User(company)
        user1.username = 'jCollins'
        user1.name = 'Jacob Collins'
        user1.set_password('password1')
        user1.is_admin = True
        user1.is_active = True
        db.session.add(user1)
        db.session.commit()
        user2 = User(company)
        user2.username = 'dMcCroskey'
        user2.name = 'Dee Dee McCroskey'
        user2.set_password('password2')
        user2.is_admin = True
        user2.is_active = True
        db.session.add(user2)
        db.session.commit()
        user3 = User(company)
        user3.username = 'pNoorossana'
        user3.name = 'Paresa Noorossana'
        user3.set_password('password3')
        user3.is_admin = True
        user3.is_active = True
        db.session.add(user3)
        db.session.commit()
        user4 = User(company)
        user4.username = 'cTurner'
        user4.name = 'Chance Turner'
        user4.set_password('password4')
        user4.is_admin = True
        user4.is_active = True
        db.session.add(user4)
        db.session.commit()
        user5 = User(company)
        user5.username = 'planner'
        user5.name = 'Planner'
        user5.set_password('password')
        user5.is_admin = False
        user5.is_active = True
        db.session.add(user5)
        db.session.commit()
        user6 = User(company)
        user6.username = 'admin'
        user6.name = 'Admin'
        user6.set_password('password')
        user6.is_admin = True
        user6.is_active = True
        db.session.add(user6)
        db.session.commit()
        user7 = User(company)
        user7.username = 'tSwift'
        user7.name = 'Taylor Swift'
        user7.set_password('password5')
        user7.is_admin = False
        user7.is_active = False
        db.session.add(user7)
        db.session.commit()
        users = [user1, user2, user3, user4, user5, user6, user7]

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
                rand = randint(0,6)
                event.planner = users[rand]
                event.name = __get_company_name(x) + "'s Awesome Event " + str(y)
                event.venue = __get_company_name(x) + "'s Venue"
                event.company = company
                event.table_size = company._table_sizes[random.randrange(len(company._table_sizes))]
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
        userA = User(company)
        userA.username = 'planner'
        userA.name = 'Planner'
        userA.set_password('password')
        userA.is_admin = False
        userA.is_active = True
        db.session.add(userA)
        db.session.commit()
        userB = User(company)
        userB.username = 'admin'
        userB.name = 'Admin'
        userB.set_password('password')
        userB.is_admin = True
        userB.is_active = True
        db.session.add(userB)
        db.session.commit()
        userC = User(company)
        userC.username = 'fired planner'
        userC.name = 'Fired Planner'
        userC.set_password('password')
        userC.is_admin = False
        userC.is_active = False
        db.session.add(userC)
        db.session.commit()
        users2 = [userA, userB, userC]

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
                rand = randint(0,2)
                event.planner = users2[rand]
                event.name = __get_company_name(x) + "'s Awesome Event " + str(y)
                event.venue = __get_company_name(x) + "'s Venue"
                event.company = company
                event.table_size = company._table_sizes[random.randrange(len(company._table_sizes))]
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
        

