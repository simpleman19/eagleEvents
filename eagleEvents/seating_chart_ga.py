import random

from eagleEvents.models import SeatingPreference
from eagleEvents.models.table import Table
from deap import algorithms
from deap import base
from deap import creator
from deap import tools
from math import floor, ceil
import itertools
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from numpy import max, mean, min, std
from multiprocessing import Pool

INIT_PCT_GUESS, CXPB, MUTPB, INDPB, TOURNSIZE, NIND, NGEN = 0, 0.55, 0.2, 0.2, 6, 200, 60
HALL_OF_FAME_SIZE = 60

toolbox = base.Toolbox()

creator.create("FitnessMulti", base.Fitness, weights=(-0.2, 1.0))
creator.create("Individual", list, fitness=creator.FitnessMulti)


# See http://www.rubicite.com/Tutorials/GeneticAlgorithms/CrossoverOperators/Order1CrossoverOperator.aspx
def table_crossover(ind1, ind2):
    size = min([len(ind1), len(ind2)])
    num1, num2, in_out = random.sample(range(0, size), 3)
    start = min([num1, num2])
    stop = max([num1, num2])

    swaps = {}
    child1, child2 = toolbox.clone(ind1), toolbox.clone(ind2)
    for i in range(start, stop):
        if child1[i] != child2[i] and child1[i] != -1:
            swaps[child1[i]] = child2[i]
    for k, v in swaps.items():
        first_1, second_1 = child1.index(k), child1.index(v)
        first_2, second_2 = child2.index(k), child2.index(v)
        if first_1 != -1 and second_1 != -1 and first_2 != -1 and second_2 != -1:
            child1[first_1], child1[second_1] = child1[second_1], child1[first_1]
            child2[first_2], child2[second_2] = child2[second_2], child2[first_2]

    ind1 = child1
    ind2 = child2
    return ind1, ind2


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


def get_preferences_by_guest_number(guest_lookup, number):
    return guest_lookup[number]


def count_preferences_in_list(guest_lookup, guest_numbers, preference_number):
    count = 0
    for i in range(len(guest_numbers)):
        if guest_numbers[i] == Table.EMPTY_SEAT:
            continue
        guest_preferences = get_preferences_by_guest_number(guest_lookup, guest_numbers[i])
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


def count_dislikes_in_list(guest_lookup, guest_numbers):
    return count_preferences_in_list(guest_lookup, guest_numbers, SeatingPreference.DISLIKE.value)


def count_likes_in_list(guest_lookup, guest_numbers):
    return count_preferences_in_list(guest_lookup, guest_numbers, SeatingPreference.LIKE.value)


def evaluate(indiv_and_else):
    table_size = indiv_and_else['size']
    guest_lookup = indiv_and_else['lookup']
    individual = indiv_and_else['indiv']
    num_tables = int(ceil(len(individual) / table_size))
    dislike_score = 0
    like_score = 0
    tables_to_check = range(num_tables)
    if not valid_seating(individual):
        print("Invalid seating...")
        return 100, 0
    for t in tables_to_check:
        guests_at_table = individual[t*table_size:(t + 1)*table_size]
        dislike_score += count_dislikes_in_list(guest_lookup, guests_at_table)
        like_score += count_likes_in_list(guest_lookup, guests_at_table)
    return dislike_score, like_score


def count_preferences(guest_dict, seating_preference):
    count = 0
    for number, guest_preference_dict in guest_dict.items():
        if guest_preference_dict is None:
            continue
        for other_number, preference_number in guest_preference_dict.items():
            if preference_number == seating_preference.value:
                count += 1
    return count


def guest_list_to_nested_dict(guests):
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


def update_fitnesses(lookup_and_size, population):
    for item, indiv in zip(lookup_and_size, population):
        item["indiv"] = indiv
    fitnesses = toolbox.map(evaluate, lookup_and_size)
    for ind, fit in zip(population, fitnesses):
        ind.fitness.values = fit


def crossover_and_mutate(toolbox, offspring):
    return algorithms.varOr(list(offspring), toolbox, cxpb=CXPB, mutpb=MUTPB, lambda_=NIND)


def update_stats(mstats, logbook, generation_number, population):
    record = mstats.compile(population)
    logbook.record(gen=generation_number, **record)


def init_population(pcls, ind_init, ind_guess_func, n, pct_heuristic):
    global toolbox
    heuristics = list([creator.Individual(ind_guess_func()) for _ in range(floor(n * pct_heuristic))])
    randoms = list(creator.Individual(toolbox.indices()) for _ in range(n - len(heuristics)))
    return heuristics + randoms


def should_terminate(hall_of_fame, generation_number, total_likes):
    found_optimal_solution = len(hall_of_fame) > 0 and hall_of_fame[0].fitness.values == (0, total_likes)
    return found_optimal_solution or generation_number > NGEN


def do_generation(hall_of_fame, lookup_and_size, population):
    # from http://deap.readthedocs.io/en/master/tutorials/basic/part2.html#variations
    offspring = toolbox.select(population, len(population))
    offspring = list(toolbox.map(toolbox.clone, offspring))

    del offspring[-HALL_OF_FAME_SIZE:]
    offspring.extend(hall_of_fame)

    offspring = crossover_and_mutate(toolbox, offspring)

    invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
    update_fitnesses(lookup_and_size, invalid_ind)

    return offspring


pool = Pool()
toolbox.register("map", pool.map)


def get_seating_chart_tables(event, log_output=False, collect_stats=False):
    global toolbox
    if event._guests is None or len(event._guests) == 0:
        raise ValueError("No guests for this event!")
    if event.table_size is None:
        raise ValueError("No table_size for this event!")
    if event.percent_extra_seats is None:
        raise ValueError("No percent_extra_seats for this event!")
    log_output = log_output
    event = event
    guest_numbers = [x.number for x in event._guests] if event._guests is not None else []
    guest_lookup = guest_list_to_nested_dict(event._guests)
    total_like_preferences = count_preferences(guest_lookup, SeatingPreference.LIKE)
    total_dislike_preferences = count_preferences(guest_lookup, SeatingPreference.DISLIKE)

    num_extra_seats = floor(len(event._guests) * event.percent_extra_seats)
    # account for table size
    num_extra_seats = num_extra_seats + (
                event.table_size.size - (len(event._guests) + num_extra_seats) % event.table_size.size)
    table_assignments = guest_numbers + [Table.EMPTY_SEAT for _ in range(num_extra_seats)]
    num_tables = ceil(len(table_assignments) / event.table_size.size)
    table_size = event.table_size.size
    lookup_and_size = [{"size": table_size, "lookup": guest_lookup, "indiv": []} for i in
                            range(NIND)]
    hall_of_fame = []

    if collect_stats:
        dislike_stats = tools.Statistics(lambda ind: ind.fitness.values[0])
        like_stats = tools.Statistics(lambda ind: ind.fitness.values[1])
        mstats = tools.MultiStatistics(dislike=dislike_stats, like=like_stats)
        mstats.register("avg", mean)
        mstats.register("std", std)
        mstats.register("min", min)
        mstats.register("max", max)
        logbook = tools.Logbook()
        logbook.header = "gen", "dislike", "like"
        logbook.chapters["dislike"].header = "avg", "std", "min", "max"
        logbook.chapters["like"].header = "avg", "std", "min", "max"

    # Create seed
    heuristic = []
    for guest_number in random.sample(guest_numbers, len(guest_numbers)):
        if guest_number == Table.EMPTY_SEAT:
            heuristic.append(guest_number)
            continue
        if guest_number in heuristic:
            continue
        heuristic.append(guest_number)
        pref_dict = guest_lookup[guest_number]
        if pref_dict is None:
            continue
        for other_guest_num, seating_pref_value in pref_dict.items():
            if seating_pref_value == SeatingPreference.LIKE.value and not (other_guest_num in heuristic):
                heuristic.append(other_guest_num)
    heuristic += [Table.EMPTY_SEAT for _ in range(num_extra_seats)]

    toolbox.register("evaluate", evaluate)
    toolbox.register("select", tools.selTournament, tournsize=TOURNSIZE, fit_attr="fitness")
    toolbox.register("mate", table_crossover)
    creator.create("FitnessMulti", base.Fitness, weights=(-0.2, 1.0))
    creator.create("Individual", list, fitness=creator.FitnessMulti)
    toolbox.register("indices", random.sample, table_assignments, len(table_assignments))
    toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.indices)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("population_guess", init_population, list, creator.Individual, heuristic)
    toolbox.register("mutate", tools.mutShuffleIndexes, indpb=INDPB)

    pop = toolbox.population_guess(n=NIND, pct_heuristic=INIT_PCT_GUESS)

    # Evaluate the first generation
    update_fitnesses(lookup_and_size, pop)
    if collect_stats:
        update_stats(mstats, logbook, 0, pop)

    generation_number = 1
    while not should_terminate(hall_of_fame, generation_number, total_like_preferences) and generation_number <= NGEN:
        pop[:] = do_generation(hall_of_fame, lookup_and_size, pop)
        if collect_stats:
            update_stats(mstats, logbook, generation_number, pop)
        pop.extend(hall_of_fame)
        hall_of_fame = sorted(pop, key=lambda indiv: indiv.fitness.values[1] - (indiv.fitness.values[0] * 2),
                                   reverse=True)[:HALL_OF_FAME_SIZE]
        if log_output:
            print("Generation: {}".format(generation_number))
            print("Current Best: {a} dislikes, {b} likes".format(a=hall_of_fame[0].fitness.values[0],
                                                                 b=hall_of_fame[0].fitness.values[1]))
        generation_number += 1

    winner = hall_of_fame[0]
    tables = []
    for t in range(num_tables):
        table = Table(event)
        table.number = t + 1
        guest_numbers_at_table = winner[t * event.table_size.size: (t + 1) * event.table_size.size]
        table.guests = list(filter(lambda g: g.number in guest_numbers_at_table, event._guests))
        tables.append(table)
    return tables, logbook, winner, total_like_preferences, total_dislike_preferences

