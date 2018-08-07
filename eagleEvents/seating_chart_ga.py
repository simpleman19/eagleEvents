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
    INIT_PCT_GUESS, CXPB, MUTPB, INDPB, TOURNSIZE, NIND, NGEN = 0, 0.5, 0.25, 0.2, 3, 400, 50
    HALL_OF_FAME_SIZE = 50
    COLLECT_STATS = False

    def __init__(self, event, log_output=False):
        if event._guests is None or len(event._guests) == 0:
            raise ValueError("No guests for this event!")
        if event.table_size is None:
            raise ValueError("No table_size for this event!")
        if event.percent_extra_seats is None:
            raise ValueError("No percent_extra_seats for this event!")
        self.log_output = log_output
        self.event = event
        self.guest_numbers = [x.number for x in event._guests] if event._guests is not None else []
        self.guest_lookup = self.guest_list_to_nested_dict(self.event._guests)
        self.total_like_preferences = self.count_preferences(self.guest_lookup, SeatingPreference.LIKE)
        self.total_dislike_preferences = self.count_preferences(self.guest_lookup, SeatingPreference.DISLIKE)

        self.num_guests = len(self.guest_numbers)
        num_extra_seats = floor(len(event._guests) * event.percent_extra_seats)
        # account for table size
        self.num_extra_seats = num_extra_seats + (event.table_size.size - (len(event._guests) + num_extra_seats) % event.table_size.size)
        self.table_assignments = self.guest_numbers + [Table.EMPTY_SEAT for _ in range(self.num_extra_seats)]
        self.num_tables = ceil(len(self.table_assignments) / event.table_size.size)
        self.toolbox = base.Toolbox()
        self.hall_of_fame = []

    def setup(self):
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
        creator.create("FitnessMulti", base.Fitness, weights=(-0.2, 1.0))
        creator.create("Individual", list, fitness=creator.FitnessMulti)

        self.toolbox.register("indices", random.sample, self.table_assignments, len(self.table_assignments))
        self.toolbox.register("individual", tools.initIterate, creator.Individual,
                              self.toolbox.indices)

    def population(self):
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)
        self.toolbox.register("population_guess", self.init_population, list, creator.Individual, self.get_individual_guess)

    def get_individual_guess(self):
        heuristic = []
        for guest_number in random.sample(self.guest_numbers, len(self.guest_numbers)):
            if guest_number == Table.EMPTY_SEAT:
                heuristic.append(guest_number)
                continue
            if guest_number in heuristic:
                continue
            heuristic.append(guest_number)
            pref_dict = self.guest_lookup[guest_number]
            if pref_dict is None:
                continue
            for other_guest_num, seating_pref_value in pref_dict.items():
                if seating_pref_value == SeatingPreference.LIKE.value and not (other_guest_num in heuristic):
                    heuristic.append(other_guest_num)
        heuristic += [Table.EMPTY_SEAT for _ in range(self.num_extra_seats)]
        return heuristic

    def init_population(self, pcls, ind_init, ind_guess_func, n, pct_heuristic):
        heuristics = list([creator.Individual(ind_guess_func()) for _ in range(floor(n * pct_heuristic))])
        randoms = list(creator.Individual(self.toolbox.indices()) for _ in range(n - len(heuristics)))
        return heuristics + randoms

    def evaluation(self):
        self.toolbox.register("evaluate", self.evaluate)

    def selection(self):
        self.toolbox.register("select", tools.selTournament, tournsize=self.TOURNSIZE, fit_attr="fitness")

    def crossover(self):
        self.toolbox.register("mate", self.table_crossover)

    # See http://www.rubicite.com/Tutorials/GeneticAlgorithms/CrossoverOperators/Order1CrossoverOperator.aspx
    def table_crossover(self, ind1, ind2):
        size = min([len(ind1), len(ind2)])
        num1, num2, in_out = random.sample(range(0, size), 3)
        start = min([num1, num2])
        stop = max([num1, num2])

        swaps = {}
        child1, child2 = self.toolbox.clone(ind1), self.toolbox.clone(ind2)
        for i in range(start, stop):
            if random.randint(0, 3) == 0:
                if child1[i] != child2[i] and child1[i] != -1 and child2[i] != -1:
                    swaps[child1[i]] = child2[i]
        for k, v in swaps.items():
            first_1, first_2 = -1, -1
            second_1, second_2 = -1, -1
            for i in range(size):
                if child1[i] == v:
                    first_1 = i
                elif child1[i] == k:
                    second_1 = i
                if child2[i] == k:
                    first_2 = i
                elif child2[i] == v:
                    second_2 = i
                if first_1 != -1 and second_1 != -1 and first_2 != -1 and second_2 != -1:
                    break
            if first_1 != -1 and second_1 != -1 and first_2 != -1 and second_2 != -1:
                child1[first_1], child1[second_1] = child1[second_1], child1[first_1]
                child2[first_2], child2[second_2] = child2[second_2], child2[first_2]

        ind1 = child1
        ind2 = child2
        return ind1, ind2

    def mutation(self):
        self.toolbox.register("mutate", tools.mutShuffleIndexes, indpb=self.INDPB)

    def statistics(self):
        dislike_stats = tools.Statistics(lambda ind: ind.fitness.values[0])
        like_stats = tools.Statistics(lambda ind: ind.fitness.values[1])
        self.mstats = tools.MultiStatistics(dislike=dislike_stats, like=like_stats)
        self.mstats.register("avg", mean)
        self.mstats.register("std", std)
        self.mstats.register("min", min)
        self.mstats.register("max", max)
        self.logbook = tools.Logbook()
        self.logbook.header = "gen", "dislike", "like"
        self.logbook.chapters["dislike"].header = "avg", "std", "min", "max"
        self.logbook.chapters["like"].header = "avg", "std", "min", "max"

    def should_terminate(self, population, generation_number):
        return False
        found_optimal_solution = len(self.hall_of_fame) > 0 and self.hall_of_fame[0].fitness.values == (0, self.total_like_preferences)
        return found_optimal_solution or generation_number > self.NGEN

    def update_fitnesses(self, population):
        fitnesses = self.toolbox.map(self.toolbox.evaluate, population)
        for ind, fit in zip(population, fitnesses):
            ind.fitness.values = fit

    def update_stats(self, generation_number, population):
        if hasattr(self, 'mstats'):
            record = self.mstats.compile(population)
            self.logbook.record(gen=generation_number, **record)

    # from http://deap.readthedocs.io/en/master/overview.html#algorithms
    def do_generations(self):
        pop = self.toolbox.population_guess(n=self.NIND, pct_heuristic=self.INIT_PCT_GUESS)

        # Evaluate the first generation
        self.update_fitnesses(pop)
        self.update_stats(0, pop)

        generation_number = 1
        while not self.should_terminate(pop, generation_number) and generation_number <= self.NGEN:
            pop[:] = self.do_generation(pop)
            self.update_stats(generation_number, pop)
            self.update_hall_of_fame(pop)
            if self.log_output:
                print("Generation: {}".format(generation_number))
                print("Current Best: {a} dislikes, {b} likes".format(a=self.hall_of_fame[0].fitness.values[0],
                                                                     b=self.hall_of_fame[0].fitness.values[1]))
            generation_number += 1
        return pop

    def update_hall_of_fame(self, pop):
        self.hall_of_fame = sorted(pop, key=lambda indiv: indiv.fitness.values[1] - (indiv.fitness.values[0] * 2),
                                   reverse=True)[:self.HALL_OF_FAME_SIZE]

    def get_seating_chart_tables(self):
        self.setup()
        population = self.do_generations()
        winner = self.hall_of_fame[0]
        tables = []
        for t in range(self.num_tables):
            table = Table(self.event)
            table.number = t + 1
            guest_numbers_at_table = winner[t * self.event.table_size.size: (t + 1) * self.event.table_size.size]
            table.guests = list(filter(lambda g: g.number in guest_numbers_at_table, self.event._guests))
            tables.append(table)
        return tables

    def do_generation(self, population):
        # from http://deap.readthedocs.io/en/master/tutorials/basic/part2.html#variations
        offspring = self.toolbox.select(population, len(population))
        offspring = list(self.toolbox.map(self.toolbox.clone, offspring))

        for good_individual in list(self.hall_of_fame):
            offspring.append(good_individual)

        offspring = self.crossover_and_mutate(offspring)

        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        self.update_fitnesses(invalid_ind)

        return offspring

    def crossover_and_mutate(self, offspring):
        return algorithms.varOr(list(offspring), self.toolbox, cxpb=self.CXPB, mutpb=self.MUTPB, lambda_=self.NIND)

    @staticmethod
    def valid_seating(individual):
        valid = True
        seen = set()
        for i in individual:
            if i != -1 and i in seen:
                valid = False
            seen.add(i)
        if len(seen) != max(individual) + 1:
            valid = False
        return valid

    def evaluate(self, individual):
        dislike_score = 0
        like_score = 0
        tables_to_check = range(self.num_tables)
        if not self.valid_seating(individual):
            print("Invalid seating...")
            return 100, 0
        for t in tables_to_check:
            guests_at_table = individual[t*self.event.table_size.size:(t + 1)*self.event.table_size.size]
            dislike_score += self.count_dislikes_in_list(guests_at_table)
            like_score += self.count_likes_in_list(guests_at_table)
        return dislike_score, like_score

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
                    pref_dict[pref.other_guest.number] = pref.preference.value
            else:
                pref_dict = None
            guests_dict[guest.number] = pref_dict
        return guests_dict

    def count_dislikes_in_list(self, guest_numbers):
        return self.count_preferences_in_list(guest_numbers, SeatingPreference.DISLIKE.value)

    def count_likes_in_list(self, guest_numbers):
        return self.count_preferences_in_list(guest_numbers, SeatingPreference.LIKE.value)

    def count_preferences_in_list(self, guest_numbers, preference_number):
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
                if not (guest_numbers[j] in guest_preferences):
                    continue
                pref = guest_preferences[guest_numbers[j]]
                if not (pref is None) and pref == preference_number:
                    count += 1
        return count

    def get_preferences_by_guest_number(self, number):
        return self.guest_lookup[number]

    def count_preferences(self, guest_dict, seating_preference):
        count = 0
        for number, guest_preference_dict in guest_dict.items():
            if guest_preference_dict is None:
                continue
            for other_number, preference_number in guest_preference_dict.items():
                if preference_number == seating_preference.value:
                    count += 1
        return count
