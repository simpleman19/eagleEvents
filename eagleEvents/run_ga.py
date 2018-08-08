import time
from sqlalchemy_utils import UUIDType

from eagleEvents.seating_chart_ga import get_seating_chart_tables
from eagleEvents.models import Event, SeatingPreference


def run():
    start = time.time()
    tables, logbook, best, total_likes, total_dislikes = get_seating_chart_tables(Event.query.get('3508863751a449b28799cc1b657f5890'), log_output=False, collect_stats=True)
    end = time.time()
    print(logbook)
    print("Execution time: {time}".format(time=end-start))
    print("Number of likes: {likes}\nNumber of dislikes: {dislikes}".format(
        likes=total_likes, dislikes=total_dislikes))
    print("Ending best Pareto front: {a} dislikes, {b} likes".format(a=best.fitness.values[0], b=best.fitness.values[1]))
    #for t in tables:
    #    print("Table {number}".format(number=t.number))
    #    for g in t.guests:
    #        print("Guest {number}".format(number=g.number))
    #        for p in g.seating_preferences:
    #            pref_display = p.preference.name
    #            if not(p.other_guest is None):
    #                print("\t{pref} {other}".format(pref=pref_display, other=p.other_guest.number))
    #    print("\n")

