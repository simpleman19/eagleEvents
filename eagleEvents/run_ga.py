from eagleEvents.seating_chart_ga import SeatingChartGA
from eagleEvents.models import Event
from eagleEvents import db

def get_event():
    return Event.query.first()

def run():
    ga = SeatingChartGA(get_event())
    ga.COLLECT_STATS = True

    ga.setup()
    ga.do_generations()
    print(ga.logbook)
