from eagleEvents.models import company, user
from eagleEvents import db
from flask_sqlalchemy import SQLAlchemy

def mock_db(monkeypatch):
    db = SQLAlchemy()
    monkeypatch.setattr(db, 'Model', {})
    return db

def test_thing():
  assert 1 == 1

def test_when_getting_event_planners_then_it_returns_all_users(monkeypatch):
    db = mock_db(monkeypatch)
    c = company.Company()
    mocklist = [user.User(company)]
    monkeypatch.setattr(c, 'users', mocklist)
    assert(len(c.get_event_planners()) == 1)
