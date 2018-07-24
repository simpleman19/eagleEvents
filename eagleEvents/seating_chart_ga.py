import random
from eagleEvents.models.table import Table
from deap import base
from deap import creator
from deap import tools
from math import floor


class SeatingChartGA():

    def __init__(self, event):
        self.event = event
        self.guest_numbers = [x.number for x in event._guests] if event._guests is not None else []
        self.num_guests = len(self.guest_numbers)
        num_extra_seats = floor(self.num_guests * event.percent_extra_seats)
        self.table_assignments = self.guest_numbers + [Table.EMPTY_SEAT for x in range(num_extra_seats)]
        self.toolbox = base.Toolbox()


    def initialization(self):
        creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMin)

        self.toolbox.register("indices", random.sample, self.table_assignments, len(self.table_assignments))
        self.toolbox.register("individual", tools.initIterate, creator.Individual,
                              self.toolbox.indices)

    def population(self):
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)

