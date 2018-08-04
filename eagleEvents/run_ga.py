import time
from sqlalchemy_utils import UUIDType

from eagleEvents.seating_chart_ga import SeatingChartGA
from eagleEvents.models import Event, SeatingPreference


def run():
    ga = SeatingChartGA(Event.query.get('3508863751a449b28799cc1b657f5890'))
    ga.COLLECT_STATS = True

    ga.setup()
    start = time.time()
    tables = ga.get_seating_chart_tables()
    end = time.time()
    print(ga.logbook)
    print("Execution time: {time}".format(time=end-start))
    print("Number of likes: {likes}\nNumber of dislikes: {dislikes}".format(
        likes=ga.total_like_preferences, dislikes=ga.total_dislike_preferences))
    #for t in tables:
    #    print("Table {number}".format(number=t.number))
    #    for g in t.guests:
    #        print("Guest {number}".format(number=g.number))
    #        for p in g.seating_preferences:
    #            pref_display = p.preference.name
    #            if not(p.other_guest is None):
    #                print("\t{pref} {other}".format(pref=pref_display, other=p.other_guest.number))
    #    print("\n")

