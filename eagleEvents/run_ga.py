import time

from eagleEvents.seating_chart_ga import SeatingChartGA
from eagleEvents.models import Event

def run():
    ga = SeatingChartGA(Event.query.first())
    ga.COLLECT_STATS = True

    ga.setup()
    start = time.time()
    ga.do_generations()
    end = time.time()
    print(ga.logbook)
    print("Execution time: {time}".format(time=end-start))
