import os
import random
import subprocess
import sys

from flask_script import Manager, Command
from livereload import Server

from config import DevelopmentConfig
from eagleEvents import create_app, db

manager = Manager(create_app)

root_path = os.path.dirname(os.path.abspath(__file__))


def _make_context():
    return dict(app=manager.app, db=db)


class LiveReloadServer(Command):
    def run(self):
        app = manager.app
        app.debug = True
        server = Server(app.wsgi_app)
        server.serve()


@manager.option('-d', '--drop_first', help='Drop tables first?')
def createdb(drop_first=True):
    """Creates the database."""
    db.session.commit()
    if drop_first:
        db.drop_all()
    db.create_all()


@manager.command
def test():
    """Run unit tests"""
    tests = subprocess.call(['python', '-m', 'pytest'])
    sys.exit(tests)


@manager.command
def resettobase():
    db.session.commit()
    db.drop_all()
    db.create_all()
    # TODO add call for generation


manager.add_command("livereload", LiveReloadServer)

if __name__ == '__main__':
    manager.run()
