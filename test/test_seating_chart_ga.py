import math

import pytest
from deap import creator
from numpy import count_nonzero, array_equal

from eagleEvents.seating_chart_ga import SeatingChartGA
from eagleEvents.models import Company, Customer, Event, Guest, TableSize, Table, SeatingPreferenceTable, \
    SeatingPreference
from flaky import flaky
from flask_sqlalchemy import SQLAlchemy
from random import random

def mock_db(monkeypatch):
    db = SQLAlchemy()
    monkeypatch.setattr(db, 'Model', {})
    return db


def mock_event(monkeypatch):
    db = mock_db(monkeypatch)
    company = Company()
    c = Customer(company)
    e = Event(c)
    ts = TableSize(company, 4)
    mock_guests = []
    for x in range(10):
        g = Guest(db)
        g.number = x
        mock_guests.append(g)

    monkeypatch.setattr(e, "_guests", mock_guests)
    monkeypatch.setattr(e, "percent_extra_seats", .5)
    monkeypatch.setattr(e, 'table_size', ts)
    return e

def get_empty_seat_count(event):
    num_empty_seats = math.floor(len(event._guests) * event.percent_extra_seats)
    # account for table size
    num_empty_seats = num_empty_seats + (event.table_size.size - (len(event._guests) + num_empty_seats) % event.table_size.size)
    return num_empty_seats

def all_in_list_once(numbers_expected, actual_list):
    already_checked = []
    for x in actual_list:
        if x == Table.EMPTY_SEAT:
            continue
        assert not (x in already_checked)
        assert x in numbers_expected
        already_checked.append(x)

##
# Initialization
##


@pytest.mark.filterwarnings('ignore::RuntimeWarning')
def test_when_initializing_then_it_returns_a_list_containing_all_guest_numbers(monkeypatch):
    e = mock_event(monkeypatch)
    guest_numbers = [x.number for x in e._guests]

    ga = SeatingChartGA(e)
    ga.initialization()
    result = ga.toolbox.individual()

    all_in_list_once(guest_numbers, result)


@pytest.mark.filterwarnings('ignore::RuntimeWarning')
def test_when_initializing_with_even_percent_then_it_returns_a_list_containing_enough_empty_seats(monkeypatch):
    e = mock_event(monkeypatch)

    monkeypatch.setattr(e, "percent_extra_seats", .5)
    num_empty_seats = get_empty_seat_count(e)
    ga = SeatingChartGA(e)
    ga.initialization()

    result = ga.toolbox.individual()

    count = len(list(filter(lambda x: x == Table.EMPTY_SEAT, result)))
    assert count == num_empty_seats


@pytest.mark.filterwarnings('ignore::RuntimeWarning')
def test_when_initializing_with_odd_percent_then_it_returns_a_list_containing_enough_empty_seats(monkeypatch):
    e = mock_event(monkeypatch)
    monkeypatch.setattr(e, "percent_extra_seats", .83)
    num_empty_seats = get_empty_seat_count(e)
    ga = SeatingChartGA(e)
    ga.initialization()

    result = ga.toolbox.individual()

    count = len(list(filter(lambda x: x == Table.EMPTY_SEAT, result)))
    assert count == num_empty_seats

@pytest.mark.filterwarnings('ignore::RuntimeWarning')
def test_when_constructing_then_it_uses_the_correct_count_of_like_preferences(monkeypatch):
    e = mock_event(monkeypatch)
    db = mock_db(monkeypatch)
    mock_guests = []
    for x in range(10):
        g = Guest(db)
        g.number = x
        mock_guests.append(g)

    # First guest likes 5 people
    mock_seating_prefs = []
    for x in range(5):
        mock_seating_prefs.append(SeatingPreferenceTable(mock_guests[0], mock_guests[x + 1], SeatingPreference.LIKE))
    monkeypatch.setattr(mock_guests[0], "seating_preferences", mock_seating_prefs)

    monkeypatch.setattr(e, "_guests", mock_guests)

    ga = SeatingChartGA(e)


    assert ga.total_like_preferences == 5

##
# Population
##


@pytest.mark.filterwarnings('ignore::RuntimeWarning')
def test_when_populating_then_it_returns_a_list_of_individuals(monkeypatch):
    e = mock_event(monkeypatch)

    ga = SeatingChartGA(e)
    ga.initialization()
    ga.population()
    result = ga.toolbox.population(n=100)
    assert len(result) == 100


@pytest.mark.filterwarnings('ignore::RuntimeWarning')
def test_when_populating_then_it_returns_individuals_containing_all_guest_numbers(monkeypatch):
    e = mock_event(monkeypatch)
    guest_numbers = [x.number for x in e._guests]

    ga = SeatingChartGA(e)
    ga.initialization()
    ga.population()
    result = ga.toolbox.population(n=100)

    all_in_list_once(guest_numbers, result[25])


@pytest.mark.filterwarnings('ignore::RuntimeWarning')
def test_when_populating_with_even_percent_then_it_returns_individuals_containing_enough_empty_seats(monkeypatch):
    e = mock_event(monkeypatch)

    monkeypatch.setattr(e, "percent_extra_seats", .5)
    num_empty_seats = get_empty_seat_count(e)
    ga = SeatingChartGA(e)
    ga.initialization()
    ga.population()

    result = ga.toolbox.population(n=100)

    count = len(list(filter(lambda x: x == Table.EMPTY_SEAT, result[25])))
    assert count == num_empty_seats


@pytest.mark.filterwarnings('ignore::RuntimeWarning')
def test_when_populating_with_odd_percent_then_it_returns_individuals_containing_enough_empty_seats(monkeypatch):
    e = mock_event(monkeypatch)
    monkeypatch.setattr(e, "percent_extra_seats", .83)
    num_empty_seats = get_empty_seat_count(e)
    ga = SeatingChartGA(e)
    ga.initialization()
    ga.population()

    result = ga.toolbox.population(n=100)

    count = len(list(filter(lambda x: x == Table.EMPTY_SEAT, result[25])))
    assert count == num_empty_seats


@pytest.mark.filterwarnings('ignore::RuntimeWarning')
def test_when_calling_get_individual_guess_then_it_returns_individuals_containing_all_guest_numbers(monkeypatch):
    e = mock_event(monkeypatch)
    guest_numbers = [x.number for x in e._guests]

    ga = SeatingChartGA(e)
    ga.initialization()
    ga.population()
    result = ga.toolbox.population_guess(n=100, pct_heuristic=1)

    all_in_list_once(guest_numbers, result[25])


@pytest.mark.filterwarnings('ignore::RuntimeWarning')
def test_when_calling_get_individual_guess_then_it_returns_individuals_containing_enough_empty_seats(monkeypatch):
    e = mock_event(monkeypatch)
    monkeypatch.setattr(e, "percent_extra_seats", .83)
    num_empty_seats = get_empty_seat_count(e)
    ga = SeatingChartGA(e)
    ga.initialization()
    ga.population()

    result = ga.toolbox.population_guess(n=100, pct_heuristic=1)

    count = len(list(filter(lambda x: x == Table.EMPTY_SEAT, result[25])))
    assert count == num_empty_seats


##
# Evaluation
##

@pytest.mark.filterwarnings('ignore::RuntimeWarning')
def test_when_calling_count_dislikes_at_table_then_it_returns_correct_count(monkeypatch):
    e = mock_event(monkeypatch)
    db = mock_db(monkeypatch)
    mock_guests = []
    for x in range(10):
        g = Guest(db)
        g.number = x
        mock_guests.append(g)

    # First guest hates everyone
    mock_seating_prefs = []
    for x in range(9):
        mock_seating_prefs.append(SeatingPreferenceTable(mock_guests[0], mock_guests[x+1], SeatingPreference.DISLIKE))
    monkeypatch.setattr(mock_guests[0], "seating_preferences", mock_seating_prefs)

    monkeypatch.setattr(e, "_guests", mock_guests)

    ga = SeatingChartGA(e)
    ga.initialization()
    ga.population()
    ga.evaluation()

    individual = ga.toolbox.population(n=1)[0]
    individual_without_empty_seats = list(filter(lambda x: x != Table.EMPTY_SEAT, individual))

    result = ga.count_dislikes_in_list(individual)

    assert result == len(individual_without_empty_seats) - 1

@pytest.mark.filterwarnings('ignore::RuntimeWarning')
def test_when_calling_count_likes_at_table_then_it_returns_correct_count(monkeypatch):
    e = mock_event(monkeypatch)
    db = mock_db(monkeypatch)
    mock_guests = []
    for x in range(10):
        g = Guest(db)
        g.number = x
        mock_guests.append(g)

    # First guest likes 5 people
    mock_seating_prefs = []
    for x in range(5):
        mock_seating_prefs.append(SeatingPreferenceTable(mock_guests[0], mock_guests[x+1], SeatingPreference.LIKE))
    monkeypatch.setattr(mock_guests[0], "seating_preferences", mock_seating_prefs)

    monkeypatch.setattr(e, "_guests", mock_guests)

    ga = SeatingChartGA(e)
    ga.initialization()
    ga.population()
    ga.evaluation()

    individual = ga.toolbox.population(n=1)[0]

    result = ga.count_likes_in_list(individual)

    assert result == 5


@pytest.mark.filterwarnings('ignore::RuntimeWarning')
def test_when_calling_evaluate_it_returns_a_tuple_containing_the_count_of_dislikes_at_all_tables(monkeypatch):
    e = mock_event(monkeypatch)

    ga = SeatingChartGA(e)
    ga.initialization()
    ga.population()
    ga.evaluation()

    def mock_count(_):
        return 2
    monkeypatch.setattr(ga, "count_dislikes_in_list", mock_count)

    individual = ga.toolbox.population(n=1)[0]
    score = ga.evaluate(individual)

    assert score[0] == 2 * ga.num_tables

@pytest.mark.filterwarnings('ignore::RuntimeWarning')
def test_when_calling_evaluate_it_returns_a_tuple_containing_the_count_of_likes_at_all_tables(monkeypatch):
    e = mock_event(monkeypatch)

    ga = SeatingChartGA(e)
    ga.initialization()
    ga.population()
    ga.evaluation()

    def mock_count(_):
        return 5
    monkeypatch.setattr(ga, "count_likes_in_list", mock_count)

    individual = ga.toolbox.population(n=1)[0]
    score = ga.evaluate(individual)

    assert score[1] == 5 * ga.num_tables


##
# Crossover / Mutate
##

@pytest.mark.filterwarnings('ignore::RuntimeWarning')
def test_when_calling_ordered_crossover_it_returns_crossovered_individuals(monkeypatch):
    e = mock_event(monkeypatch)
    db = mock_db(monkeypatch)

    ga = SeatingChartGA(e)
    ga.initialization()
    ga.population()
    ga.evaluation()
    ga.crossover()

    ind1 = creator.Individual([1, 2, 3, 4, 5, 6])
    ind2 = creator.Individual([6, 5, 4, 3, 2, 1])

    child1, child2 = ga.toolbox.mate(ind1, ind2)

    assert(len(child1) == len(child2) == len(ind1) == len(ind2))

    all_in_list_once([1, 2, 3, 4, 5, 6], child1)
    all_in_list_once([1, 2, 3, 4, 5, 6], child2)


@flaky(max_runs=5,min_passes=1)
@pytest.mark.filterwarnings('ignore::RuntimeWarning')
def test_when_calling_crossover_and_mutate_it_returns_a_mated_population(monkeypatch):
    e = mock_event(monkeypatch)
    db = mock_db(monkeypatch)
    mock_guests = []
    for x in range(100):
        g = Guest(db)
        g.number = x
        mock_guests.append(g)

    monkeypatch.setattr(e, "_guests", mock_guests)

    ga = SeatingChartGA(e)
    ga.initialization()
    ga.population()
    ga.evaluation()
    ga.crossover()
    ga.mutation()

    monkeypatch.setattr(ga, "NIND", 10)
    monkeypatch.setattr(ga, "CXPB", 1)
    monkeypatch.setattr(ga, "MUTPB", 0)

    population = ga.toolbox.population(n=10)
    mated = ga.crossover_and_mutate(population)

    assert len(population) == len(mated)
    assert any([not(array_equal(population[i], mated[i])) for i in range(len(population)) ])


@flaky(max_runs=5,min_passes=1)
@pytest.mark.filterwarnings('ignore::RuntimeWarning')
def test_when_calling_crossover_and_mutate_it_returns_a_mutated_population(monkeypatch):
    e = mock_event(monkeypatch)
    db = mock_db(monkeypatch)
    mock_guests = []
    for x in range(100):
        g = Guest(db)
        g.number = x
        mock_guests.append(g)

    monkeypatch.setattr(e, "_guests", mock_guests)

    ga = SeatingChartGA(e)
    ga.initialization()
    ga.population()
    ga.evaluation()
    ga.crossover()
    ga.mutation()

    monkeypatch.setattr(ga, "CXPB", 0)
    monkeypatch.setattr(ga, "MUTPB", 1)
    monkeypatch.setattr(ga, "NIND", 10)

    population = ga.toolbox.population(n=10)
    mutated = ga.crossover_and_mutate(population)

    assert len(population) == len(mutated)
    assert any([not (array_equal(population[i], mutated[i])) for i in range(len(population))])


##
# Termination
##


@pytest.mark.filterwarnings('ignore::RuntimeWarning')
def test_when_calling_should_terminate_it_returns_true_after_NGEN(monkeypatch):
    e = mock_event(monkeypatch)

    ga = SeatingChartGA(e)
    ga.selection()
    monkeypatch.setattr(ga, "NGEN", 10)
    monkeypatch.setattr(ga, "hall_of_fame", [])

    assert not (ga.should_terminate([], -1))
    assert not (ga.should_terminate([], 0))
    assert not (ga.should_terminate([], 9))
    assert not (ga.should_terminate([], 10))
    assert ga.should_terminate([], 11)
    assert ga.should_terminate([], 500)


##
# Generation
##


@pytest.mark.filterwarnings('ignore::RuntimeWarning')
def test_when_calling_do_generation_it_returns_offspring_with_fitness_values(monkeypatch):
    e = mock_event(monkeypatch)

    ga = SeatingChartGA(e)
    def mock_count(list):
        return (1,)
    monkeypatch.setattr(ga, "evaluate", mock_count)
    monkeypatch.setattr(ga, "NIND", 5)

    ga.setup()

    population = ga.toolbox.population(n=5)
    for ind in population:
        assert not(ind.fitness.valid)

    offspring = ga.do_generation(population)

    for ind in offspring:
        assert ind.fitness.valid
        assert count_nonzero(ind.fitness.values) == len(ind.fitness.values)


@flaky(max_runs=5,min_passes=1)
@pytest.mark.filterwarnings('ignore::RuntimeWarning')
def test_when_calling_do_generation_it_returns_offspring_not_in_the_parent_population(monkeypatch):
    e = mock_event(monkeypatch)
    db = mock_db(monkeypatch)
    mock_guests = []
    for x in range(100):
        g = Guest(db)
        g.number = x
        mock_guests.append(g)

    monkeypatch.setattr(e, "_guests", mock_guests)

    ga = SeatingChartGA(e)

    def mock_count(list):
        return float(random()),
    monkeypatch.setattr(ga, "evaluate", mock_count)
    monkeypatch.setattr(ga, "NIND", 5)
    ga.setup()

    population = ga.toolbox.population(n=5)
    for ind in population:
        assert not(ind.fitness.valid)

    offspring = ga.do_generation(population)

    assert len(population) == len(offspring)
    assert any([not (array_equal(population[i], offspring[i])) for i in range(len(population))])


@pytest.mark.filterwarnings('ignore::RuntimeWarning')
def test_when_calling_do_generations_it_uses_should_terminate_to_terminate(monkeypatch):
    e = mock_event(monkeypatch)
    was_called = False
    ga = SeatingChartGA(e)

    def mock_terminate(pop, n):
        nonlocal was_called
        was_called = True
        return True

    monkeypatch.setattr(ga, "should_terminate", mock_terminate)

    ga.setup()
    ga.do_generations()

    assert was_called


##
# Winner / Completion
##

@pytest.mark.filterwarnings('ignore::RuntimeWarning')
def test_when_calling_get_seating_chart_tables_it_returns_a_list_of_tables_with_extra_seats(monkeypatch):
    e = mock_event(monkeypatch)

    ga = SeatingChartGA(e)
    tables = ga.get_seating_chart_tables()

    assert(len(tables) * e.table_size.size == len(e._guests) + get_empty_seat_count(e))


@pytest.mark.filterwarnings('ignore::RuntimeWarning')
def test_when_calling_get_seating_chart_tables_it_returns_a_list_of_tables_containing_all_guests_once(monkeypatch):
    e = mock_event(monkeypatch)
    expected_guest_numbers = [g.number for g in e._guests]

    ga = SeatingChartGA(e)
    tables = ga.get_seating_chart_tables()
    for t in tables:
        for g in t.guests:
            assert(g.number in expected_guest_numbers)
            expected_guest_numbers.remove(g.number)
    assert len(expected_guest_numbers) == 0
