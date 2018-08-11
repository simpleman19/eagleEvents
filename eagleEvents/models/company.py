from eagleEvents.models import db
from eagleEvents.models import User
from eagleEvents.models.guest import Guest, SeatingPreference, SeatingPreferenceTable
import timeit, uuid, csv, os
from sqlalchemy_utils import UUIDType
from typing import List


class Company(db.Model):
    __tablename__ = 'company'
    id = db.Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(250), nullable=False)
    users = db.relationship('User', lazy=True)
    _table_sizes = db.relationship('TableSize', lazy=False)
    customers = db.relationship('Customer', lazy=True,
                                backref=db.backref('customer', lazy='subquery'))
    events = db.relationship('Event', lazy=True)

    # This is a little abstraction to make sizes easier to deal with but still mapped with the ORM
    @property
    def table_sizes(self) -> List[int]:
        return [ts.size for ts in self._table_sizes]

    @table_sizes.setter
    def table_sizes(self, values: List[int]):
        self._table_sizes = [TableSize(self.id, v) for v in values]

    def get_event_planners(self) -> List[User]:
        return self.users

    def process_guest_list(self, file_name, event):
        start = timeit.default_timer()
        with open(file_name) as csv_file:
            read_csv = csv.reader(csv_file, delimiter=',')
            header = next(read_csv)
            dislikes = header.count("different_table")
            like = len(header) - dislikes

            # clear out the guest list for this event
            guests_to_delete = db.session.query(Guest).filter(Guest.event_id == event.id).all()
            [db.session.delete(g) for g in guests_to_delete]
            db.session.commit()

            likes_dict = {}
            dislikes_dict = {}
            guest_dict = {}
            # read in the csv file and create a guest list
            for row in read_csv:
                g = Guest(event)
                g.id = uuid.uuid4()
                g.number = row[0]
                g.title = row[1]
                g.first_name = row[2]
                g.last_name = row[3]

                likes_dict[g.number] = []
                dislikes_dict[g.number] = []
                for i in range(4, like, 1):
                    if row[i] is not '':
                        likes_dict[g.number].append(row[i])
                        # print('Likes ', row[i])
                for j in range(like, len(header), 1):
                    if row[j] is not '':
                        dislikes_dict[g.number].append(row[j])
                        # print('Dislikes ', row[j])
                # print(' ')
                db.session.add(g)
                guest_dict[g.number] = g

        # iterate through for seating preferences for each guest
        for key, value in likes_dict.items():
            # print('likes ', key, value)
            g1 = guest_dict.get(key)
            for v in value:
                g2 = guest_dict.get(v)
                if g1 and g2:
                    pref = SeatingPreferenceTable(g1, g2, SeatingPreference.LIKE)
                    db.session.add(pref)
                else:
                    print('Guest was not found: ', g1, g2)
        for key, value in dislikes_dict.items():
            # print('dislikes ', key, value)
            g1 = guest_dict.get(key)
            for v in value:
                g2 = guest_dict.get(v)
                if g1 and g2:
                    pref = SeatingPreferenceTable(g1, g2, SeatingPreference.DISLIKE)
                    db.session.add(pref)
                else:
                    print('Guest was not found: ', g1, g2)
        db.session.commit()
        os.remove(file_name)
        stop = timeit.default_timer()
        print('Import Complete', stop - start)
        if not os.path.isfile(file_name):
            print(file_name, ' removed')
        start = timeit.default_timer()
        event.generate_seating_chart()
        stop = timeit.default_timer()
        print('Seating Chart Generated', stop-start)


class TableSize(db.Model):
    __tablename__ = 'table_sizes'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    company_id = db.Column(UUIDType(binary=False), db.ForeignKey('company.id'))
    size = db.Column(db.Integer, nullable=False)

    def __init__(self, company_id, size):
        self.company_id = company_id
        self.size = size
