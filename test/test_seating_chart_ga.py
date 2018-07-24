import math

from eagleEvents.seating_chart_ga import SeatingChartGA
from eagleEvents.models import Company, Customer, Event, Guest, Table
from flask_sqlalchemy import SQLAlchemy


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
    return e


def test_when_initializing_then_it_returns_a_list_containing_all_guest_numbers(monkeypatch):
    e = mock_event(monkeypatch)
    guest_numbers = [x.number for x in e._guests]

    ga = SeatingChartGA(e)
    ga.initialize()
    result = ga.toolbox.individual()

    already_checked = []
    for x in result:
        if x == Table.EMPTY_SEAT:
            continue
        assert not(x in already_checked)
        assert x in guest_numbers
        already_checked.append(x)


def test_when_initializing_with_even_percent_then_it_returns_a_list_containing_enough_empty_seats(monkeypatch):
    e = mock_event(monkeypatch)

    monkeypatch.setattr(e, "percent_extra_seats", .5)
    num_empty_seats = math.floor(len(e._guests) * e.percent_extra_seats)
    ga = SeatingChartGA(e)
    ga.initialize()

    result = ga.toolbox.individual()

    count = len(list(filter(lambda x: x == Table.EMPTY_SEAT, result)))
    assert count == num_empty_seats


def test_when_initializing_with_odd_percent_then_it_returns_a_list_containing_enough_empty_seats(monkeypatch):
    e = mock_event(monkeypatch)
    monkeypatch.setattr(e, "percent_extra_seats", .83)
    num_empty_seats = math.floor(len(e._guests) * e.percent_extra_seats)
    ga = SeatingChartGA(e)
    ga.initialize()

    result = ga.toolbox.individual()

    count = len(list(filter(lambda x: x == Table.EMPTY_SEAT, result)))
    assert count == num_empty_seats

