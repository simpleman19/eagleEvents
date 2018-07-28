import random

from eagleEvents.models import SeatingPreference
from eagleEvents.models.table import Table
from deap import algorithms
from deap import base
from deap import creator
from deap import tools
from math import floor, ceil
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from numpy import max, mean, min, std


class SeatingChartGA:
    PCT_TO_EVAL, CXPB, MUTPB, NIND, NGEN = 1.0, 0.5, 0.5, 50, 50
    COLLECT_STATS = False

    def __init__(self, event):
        if(event._guests is None or len(event._guests) == 0):
            raise ValueError("No guests for this event!")
        if (event.table_size is None):
            raise ValueError("No table_size for this event!")
        if (event.percent_extra_seats is None):
            raise ValueError("No percent_extra_seats for this event!")
        self.event = event
        self.guest_numbers = [x.number for x in event._guests] if event._guests is not None else []
        self.guest_lookup = self.guest_list_to_nested_dict(self.event._guests)
        self.num_guests = len(self.guest_numbers)
        #TODO round up to the nearest table
        num_extra_seats = floor(self.num_guests * event.percent_extra_seats)
        self.num_tables = ceil(num_extra_seats / event.table_size.size)
        self.table_assignments = self.guest_numbers + [Table.EMPTY_SEAT for x in range(num_extra_seats)]
        self.toolbox = base.Toolbox()

    def setup(self):
        self.num_tables_to_evaluate = floor(self.num_tables * self.PCT_TO_EVAL)
        self.initialization()
        self.population()
        self.evaluation()
        self.selection()
        self.crossover()
        self.mutation()
        if self.COLLECT_STATS:
            self.statistics()

    def pooled_map(self, fun, it, chunksize=5):
        with ThreadPoolExecutor() as executor:
            mapped = executor.map(fun, it, chunksize=5)
        return mapped

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

    def selection(self):
        self.toolbox.register("select", tools.selBest)

    def crossover(self):
        self.toolbox.register("mate", tools.cxPartialyMatched)

    def mutation(self):
        self.toolbox.register("mutate", tools.mutShuffleIndexes, indpb=0.1)

    def statistics(self):
        self.stats = tools.Statistics(lambda ind: ind.fitness.values)
        self.stats.register("avg", mean)
        self.stats.register("std", std)
        self.stats.register("min", min)
        self.stats.register("max", max)
        self.logbook = tools.Logbook()
        self.logbook.header = "gen", "avg", "std", "min", "max"

    def should_terminate(self, population, generation_number):
        return generation_number > self.NGEN

    def update_fitnesses(self, population):
        fitnesses = self.toolbox.map(self.toolbox.evaluate, population)
        for ind, fit in zip(population, fitnesses):
            ind.fitness.values = fit

    def update_stats(self, generation_number, population):
        if hasattr(self, 'stats'):
            record = self.stats.compile(population)
            self.logbook.record(gen=generation_number, **record)

    # from http://deap.readthedocs.io/en/master/overview.html#algorithms
    def do_generations(self):
        pop = self.toolbox.population(n=self.NIND)

        # Evaluate the first generation
        self.update_fitnesses(pop)
        self.update_stats(0, pop)

        generation_number = 1
        while not self.should_terminate(pop, generation_number):
            pop[:] = self.do_generation(pop)
            self.update_stats(generation_number, pop)
            generation_number += 1

        return pop

    def do_generation(self, population):
        # from http://deap.readthedocs.io/en/master/tutorials/basic/part2.html#variations
        offspring = self.toolbox.select(population, len(population))
        offspring = self.toolbox.map(self.toolbox.clone, offspring)
        offspring = self.crossover_and_mutate(offspring)
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        self.update_fitnesses(invalid_ind)

        return offspring

    def crossover_and_mutate(self, offspring):
        return algorithms.varAnd(offspring, self.toolbox, self.CXPB, self.MUTPB)

    def evaluate(self, individual):
        score = 0
        tables_to_check = range(self.num_tables)#random.sample(range(self.num_tables), self.num_tables_to_evaluate)
        for t in tables_to_check:
            guests_at_table = individual[t*self.num_tables:t*(self.num_tables+1)]
            score += self.count_dislikes_in_list(guests_at_table)
        return (score),

    def guest_list_to_nested_dict(self, guests):
        guests_dict = dict()
        for guest in guests:
            if not (guest.seating_preferences is None) and len(guest.seating_preferences) > 0:
                pref_dict = dict()
                for pref in guest.seating_preferences:
                    if pref.other_guest is None:
                        continue #FIXME: remove this before I commit
                        #raise ValueError("Cannot find other_guest with id {other_id} for seating preference {pref_id} on guest {guest_id}".format(
                        #    other_id=pref.other_guest_id,
                        #    pref_id=pref.id,
                        #    guest_id=guest.id))
                    pref_dict[pref.other_guest.number] = 1 if pref == SeatingPreference.LIKE else 0
            else:
                pref_dict = None
            guest_dict = dict([(guest.number, pref_dict) for guest in guests])
            guests_dict[guest.number] = guest_dict
        return guests_dict

    def count_dislikes_in_list(self, guest_numbers):
        count = 0
        for i in range(len(guest_numbers)):
            if guest_numbers[i] == Table.EMPTY_SEAT:
                continue
            guest_preferences = self.get_preferences_by_guest_number(guest_numbers[i])
            if guest_preferences is None or len(guest_preferences) == 0:
                continue
            for j in range(len(guest_numbers)):
                if i == j:
                    continue
                if guest_numbers[j] == Table.EMPTY_SEAT:
                    continue
                pref = guest_preferences[guest_numbers[j]]
                if not (pref is None) and pref == 0:
                    count += 1
        return count

    def get_preferences_by_guest_number(self, number):
        return self.guest_lookup[number]
