from flask import abort, Blueprint, redirect, render_template, g, request, url_for, flash

from eagleEvents import db
from eagleEvents.auth import multi_auth
from eagleEvents.models import User
event_planners_blueprint = Blueprint('event_planners', __name__)


@event_planners_blueprint.route('/listEventPlanners')
@multi_auth.login_required
def list_event_planners():
    return render_template('user.html.j2')


@event_planners_blueprint.route('/addEventPlanner', methods=['GET', 'POST'])
@multi_auth.login_required
def add_event_planner():
    if not g.current_user.is_admin:
        abort(401)
    return render_template('add-update-user.html.j2',
                           cancel_redirect=url_for('event_planners.list_event_planners'))


@event_planners_blueprint.route('/modifyEventPlanner/<userid>', methods=['GET', 'POST'])
@multi_auth.login_required
def modify_event_planner(userid):
    if not g.current_user.is_admin:
        abort(401)
    return render_template('add-update-user.html.j2', userid=userid,
                           cancel_redirect=url_for('event_planners.list_event_planners'))
