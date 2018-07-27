import math

from numpy import count_nonzero, array_equal

from eagleEvents.seating_chart_ga import SeatingChartGA
from eagleEvents.models import Company, Customer, Event, Guest, Table
from flaky import flaky
from flask_sqlalchemy import SQLAlchemy
from random import random

def mock_db(monkeypatch):
    db = SQLAlchemy()
    monkeypatch.setattr(db, 'Model', {})
    return db


def mock_event(monkeypatch):
    db = mock_db(monkeypatch)
    c = Customer(Company())
    e = Event(c)
    mock_guests = []
    for x in range(10):
        g = Guest(db)
        g.number = x
        mock_guests.append(g)

    monkeypatch.setattr(e, "_guests", mock_guests)
    monkeypatch.setattr(e, "percent_extra_seats", .5)
    monkeypatch.setattr(e, 'table_size', 4)
    return e


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


def test_when_initializing_then_it_returns_a_list_containing_all_guest_numbers(monkeypatch):
    e = mock_event(monkeypatch)
    guest_numbers = [x.number for x in e._guests]

    ga = SeatingChartGA(e)
    ga.initialization()
    result = ga.toolbox.individual()

    all_in_list_once(guest_numbers, result)


def test_when_initializing_with_even_percent_then_it_returns_a_list_containing_enough_empty_seats(monkeypatch):
    e = mock_event(monkeypatch)

    monkeypatch.setattr(e, "percent_extra_seats", .5)
    num_empty_seats = math.floor(len(e._guests) * e.percent_extra_seats)
    ga = SeatingChartGA(e)
    ga.initialization()

    result = ga.toolbox.individual()

    count = len(list(filter(lambda x: x == Table.EMPTY_SEAT, result)))
    assert count == num_empty_seats


def test_when_initializing_with_odd_percent_then_it_returns_a_list_containing_enough_empty_seats(monkeypatch):
    e = mock_event(monkeypatch)
    monkeypatch.setattr(e, "percent_extra_seats", .83)
    num_empty_seats = math.floor(len(e._guests) * e.percent_extra_seats)
    ga = SeatingChartGA(e)
    ga.initialization()

    result = ga.toolbox.individual()

    count = len(list(filter(lambda x: x == Table.EMPTY_SEAT, result)))
    assert count == num_empty_seats

##
# Population
##


def test_when_populating_then_it_returns_a_list_of_individuals(monkeypatch):
    e = mock_event(monkeypatch)

    ga = SeatingChartGA(e)
    ga.initialization()
    ga.population()
    result = ga.toolbox.population(n=100)
    assert len(result) == 100


def test_when_populating_then_it_returns_individuals_containing_all_guest_numbers(monkeypatch):
    e = mock_event(monkeypatch)
    guest_numbers = [x.number for x in e._guests]

    ga = SeatingChartGA(e)
    ga.initialization()
    ga.population()
    result = ga.toolbox.population(n=100)

    all_in_list_once(guest_numbers, result[25])


def test_when_populating_with_even_percent_then_it_returns_individuals_containing_enough_empty_seats(monkeypatch):
    e = mock_event(monkeypatch)

    monkeypatch.setattr(e, "percent_extra_seats", .5)
    num_empty_seats = math.floor(len(e._guests) * e.percent_extra_seats)
    ga = SeatingChartGA(e)
    ga.initialization()
    ga.population()

    result = ga.toolbox.population(n=100)

    count = len(list(filter(lambda x: x == Table.EMPTY_SEAT, result[25])))
    assert count == num_empty_seats


def test_when_populating_with_odd_percent_then_it_returns_individuals_containing_enough_empty_seats(monkeypatch):
    e = mock_event(monkeypatch)
    monkeypatch.setattr(e, "percent_extra_seats", .83)
    num_empty_seats = math.floor(len(e._guests) * e.percent_extra_seats)
    ga = SeatingChartGA(e)
    ga.initialization()
    ga.population()

    result = ga.toolbox.population(n=100)

    count = len(list(filter(lambda x: x == Table.EMPTY_SEAT, result[25])))
    assert count == num_empty_seats


##
# Evaluation
##

def test_when_calling_count_dislikes_at_table_then_it_returns_correct_count(monkeypatch):
    e = mock_event(monkeypatch)
    db = mock_db(monkeypatch)
    def mock_dislike(guest):
        return True
    def mock_not_dislike(guest):
        return False
    mock_guests = []
    for x in range(10):
        g = Guest(db)
        g.number = x
        # Guest 1 hates everyone
        if x == 1:
            monkeypatch.setattr(g, "dislikes", mock_dislike)
        else:
            monkeypatch.setattr(g, "dislikes", mock_not_dislike)
        mock_guests.append(g)

    monkeypatch.setattr(e, "_guests", mock_guests)

    ga = SeatingChartGA(e)
    ga.initialization()
    ga.population()
    ga.evaluation()

    individual = ga.toolbox.population(n=1)[0]
    individual_without_empty_seats = list(filter(lambda x: x != Table.EMPTY_SEAT, individual))

    result = ga.count_dislikes_in_list(individual)

    assert result == len(individual_without_empty_seats) - 1


def test_when_calling_evaluate_it_returns_a_tuple_containing_the_count_of_dislikes_at_some_tables(monkeypatch):
    e = mock_event(monkeypatch)

    ga = SeatingChartGA(e)
    ga.initialization()
    ga.population()
    ga.evaluation()

    def mock_count(list):
        return 2
    monkeypatch.setattr(ga, "count_dislikes_in_list", mock_count)

    individual = ga.toolbox.population(n=1)[0]
    score = ga.evaluate(individual)

    assert score[0] < 2 * ga.num_tables


##
# Crossover / Mutate
##


@flaky(max_runs=5,min_passes=1)
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

    monkeypatch.setattr(ga, "CXPB", 1)
    monkeypatch.setattr(ga, "MUTPB", 0)

    population = ga.toolbox.population(n=10)
    mated = ga.crossover_and_mutate(population)

    assert len(population) == len(mated)
    assert any([not(array_equal(population[i], mated[i])) for i in range(len(population)) ])


@flaky(max_runs=5,min_passes=1)
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

    population = ga.toolbox.population(n=10)
    mutated = ga.crossover_and_mutate(population)

    assert len(population) == len(mutated)
    assert any([not (array_equal(population[i], mutated[i])) for i in range(len(population))])


##
# Termination
##


def test_when_calling_should_terminate_it_returns_true_after_NGEN(monkeypatch):
    e = mock_event(monkeypatch)

    ga = SeatingChartGA(e)
    monkeypatch.setattr(ga, "NGEN", 10)

    assert not (ga.should_terminate({}, -1))
    assert not (ga.should_terminate({}, 0))
    assert not (ga.should_terminate({}, 9))
    assert not (ga.should_terminate({}, 10))
    assert ga.should_terminate({}, 11)
    assert ga.should_terminate({}, 500)


##
# Generation
##


def test_when_calling_do_generation_it_returns_offspring_with_fitness_values(monkeypatch):
    e = mock_event(monkeypatch)

    ga = SeatingChartGA(e)
    def mock_count(list):
        return (1,)
    monkeypatch.setattr(ga, "evaluate", mock_count)

    ga.setup()

    population = ga.toolbox.population(n=5)
    for ind in population:
        assert not(ind.fitness.valid)

    offspring = ga.do_generation(population)

    for ind in offspring:
        assert ind.fitness.valid
        assert count_nonzero(ind.fitness.values) == len(ind.fitness.values)


@flaky(max_runs=5,min_passes=1)
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

    ga.setup()

    population = ga.toolbox.population(n=5)
    for ind in population:
        assert not(ind.fitness.valid)

    offspring = ga.do_generation(population)

    assert len(population) == len(offspring)
    assert any([not (array_equal(population[i], offspring[i])) for i in range(len(population))])


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
