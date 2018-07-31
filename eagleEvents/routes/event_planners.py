from flask import Blueprint, render_template, g
from eagleEvents.auth import multi_auth
event_planners_blueprint = Blueprint('event_planners', __name__)


@event_planners_blueprint.route('/listEventPlanners')
@multi_auth.login_required
def list_event_planners():
    # TODO List event planners
    return render_template('user.html.j2')


@event_planners_blueprint.route('/modifyEventPlanner')
@multi_auth.login_required
def modify_event_planner():
    # TODO Modify event planner
    if not g.current_user.is_admin:
        # TODO create and insert 401 page here
        return "Not authorized"
    return render_template('add-user.html.j2', user=g.current_user)