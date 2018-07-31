from flask import abort, Blueprint, render_template, g, request, url_for
from eagleEvents.auth import multi_auth
from eagleEvents.models import User

event_planners_blueprint = Blueprint('event_planners', __name__)


@event_planners_blueprint.route('/listEventPlanners')
@multi_auth.login_required
def list_event_planners():
    # TODO List event planners
    return render_template('user.html.j2')


@event_planners_blueprint.route('/modifyEventPlanner/<user_id>', methods=['GET', 'POST'])
@multi_auth.login_required
def modify_event_planner(user_id):
    if not g.current_user.is_admin:
        abort(401)
    user = User.query.get(user_id)
    if request.method == 'GET':
        return render_template('add-update-user.html.j2', user=user,
                               cancel_redirect=url_for('event_planners.list_event_planners'))
    # TODO Modify event planner

