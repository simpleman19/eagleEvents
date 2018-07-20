from eagleEvents import db

# Import Models to make working with packages easier, not super pythonic but also not wrong
from .user import User
from .company import Company, TableSize
from .guest import Guest, SeatingPreference, SeatingPreferenceTable
from .customer import Customer
from .table import Table
from .event import Event
