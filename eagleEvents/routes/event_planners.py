from flask import Blueprint, render_template

event_planners_blueprint = Blueprint('event_planners', __name__)


@event_planners_blueprint.route('/listEventPlanners')
def list_event_planners():
    # TODO List event planners
    return render_template('user.html.j2')


@event_planners_blueprint.route('/modifyEventPlanner')
def modify_event_planner():
    # TODO Modify event planner
    return render_template('test.html.j2')