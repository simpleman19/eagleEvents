import time
from sqlalchemy_utils import UUIDType

from eagleEvents.seating_chart_ga import SeatingChartGA
from eagleEvents.models import Event, db

def run():
    event = Event.query.get('b45e38e0004946718126bd72446b76d3')
    ga = SeatingChartGA(event)
    ga.COLLECT_STATS = True

    ga.setup()
    start = time.time()
    tables = ga.get_seating_chart_tables()
    [db.session.delete(table) for table in event.tables]
    db.session.commit()
    [db.session.add(table) for table in tables]
    db.session.commit()
    end = time.time()
    print(ga.logbook)
    print("Execution time: {time}".format(time=end-start))
    for t in tables:
        print("Table {number}".format(number=t.number))
        for g in t.guests:
            print("Guest {number}".format(number=g.number))
            for p in g.seating_preferences:
                pref_display = "LIKE" if p.preference == 1 else "DISLIKE"
                if not(p.other_guest is None):
                    print("\t{pref} {other}".format(pref=pref_display, other=p.other_guest.number))
        print("\n")

