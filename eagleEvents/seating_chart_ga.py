import random

from eagleEvents.models.table import Table
from deap import base
from deap import creator
from deap import tools
from math import floor, ceil


class SeatingChartGA:

    def __init__(self, event):
        self.event = event
        self.guest_numbers = [x.number for x in event._guests] if event._guests is not None else []
        self.num_guests = len(self.guest_numbers)
        #TODO round up to the nearest table
        num_extra_seats = floor(self.num_guests * event.percent_extra_seats)
        self.num_tables = ceil(num_extra_seats / event.table_size)
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

    def evaluation(self):
        self.toolbox.register("evaluate", self.evaluate)

    def evaluate(self, individual):
        score = 0
        #TODO if this is too slow, only check a % of tables as written in the design doc
        for t in range(self.num_tables):
            guests_at_table = individual[t*self.num_tables:t*(self.num_tables+1)]
            score += self.count_dislikes_in_list(guests_at_table)
        return (score),

    def count_dislikes_in_list(self, guest_numbers):
        count = 0
        for i in range(len(guest_numbers)):
            if guest_numbers[i] == Table.EMPTY_SEAT:
                continue
            guest = self.get_guest_by_number(guest_numbers[i])
            for j in range(len(guest_numbers)):
                if i == j:
                    continue
                if guest_numbers[j] == Table.EMPTY_SEAT:
                    continue
                other_guest = self.get_guest_by_number(guest_numbers[j])
                if guest.dislikes(other_guest):
                    count += 1
        return count

    def get_guest_by_number(self, number):
        for guest in self.event._guests:
            if guest.number == number:
                return guest
        return None


