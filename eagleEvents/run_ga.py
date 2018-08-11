import time
from sqlalchemy_utils import UUIDType
from eagleEvents.seating_chart_ga import get_seating_chart_tables
from eagleEvents.models import Event, SeatingPreference, db


def run():
    event1 = "1c87aab94e44497e944b4c90728582e7"
    event2 = "938244a3f20e4dfe8095b595783b1c50"
    event3 = "fe18e325a7124420a788b389a8390d0f"
    event4 = "5fd34218-fe31-4e9c-96b4-559d034d4f77"
    start = time.time()
    tables, logbook, best, total_likes, total_dislikes = get_seating_chart_tables(Event.query.get(event4), log_output=False, collect_stats=True)
    end = time.time()
    print(logbook)
    print("Execution time: {time}".format(time=end-start))
    print("Number of likes: {likes}\nNumber of dislikes: {dislikes}".format(
        likes=total_likes, dislikes=total_dislikes))
    print("Ending best seating chart: {a} dislikes, {b} likes".format(a=best.fitness.values[0], b=best.fitness.values[1]))

    #for t in tables:
    #    print("Table {number}".format(number=t.number))
    #    for g in t.guests:
    #        print("Guest {number}".format(number=g.number))
    #        for p in g.seating_preferences:
    #            pref_display = p.preference.name
    #            if not(p.other_guest is None):
    #                print("\t{pref} {other}".format(pref=pref_display, other=p.other_guest.number))
    #    print("\n")


def run_all():
    for event in Event.query.all():
        try:
            # Removal all tables from event
            [db.session.delete(table) for table in event.tables]
            db.session.commit()

            start = time.time()
            tables, logbook, best, total_likes, total_dislikes = get_seating_chart_tables(
                event, log_output=False, collect_stats=True)

            # Commit tables to DB
            [db.session.add(table) for table in tables]
            db.session.commit()
            print("Event id: " + str(event.id))
            end = time.time()
            print(logbook)
            print("Execution time: {time}".format(time=end-start))
            print("Total dislikes: {dislikes}\tTotal likes: {likes}".format(dislikes=total_dislikes,
                                                                            likes=total_likes))
            print("Best result: {dislikes} dislikes\t{likes} likes".format(dislikes=best.fitness.values[0],
                                                                           likes=best.fitness.values[1],))
            pct_adherence = ((total_dislikes - best.fitness.values[0]) + best.fitness.values[1]) / (total_likes + total_dislikes)
            print("Best result's adherence to preferences: {pct}%".format(pct=pct_adherence))
        except Exception as e:
            print("Ga threw an exception on event: " + str(event.id))
            print(e)
