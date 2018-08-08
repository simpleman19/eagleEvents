from flask import abort, Blueprint, redirect, render_template, g, request, url_for, flash

from eagleEvents import db
from eagleEvents.auth import multi_auth
from eagleEvents.models import User
event_planners_blueprint = Blueprint('event_planners', __name__)


@event_planners_blueprint.route('/listEventPlanners')
@multi_auth.login_required
def list_event_planners():
    users = g.current_user.company.users;
    return render_template('user.html.j2', users=users)


@event_planners_blueprint.route('/addEventPlanner', methods=['GET', 'POST'])
@multi_auth.login_required
def add_event_planner():
    user = User(g.current_user.company)
    # Set defaults
    user.is_active = True
    user.is_admin = False
    if request.method == 'GET':
        return render_template('add-update-user.html.j2', user=user,
                               cancel_redirect=url_for('event_planners.list_event_planners'))
    else:
        is_valid = validate_and_save(user, request)
        if is_valid:
            flash("{name} added".format(name=user.name), "success")
            return redirect(url_for('event_planners.list_event_planners'))
        else:
            return render_template('add-update-user.html.j2', user=user,
                                   cancel_redirect=url_for('event_planners.list_event_planners'))


@event_planners_blueprint.route('/modifyEventPlanner/<user_id>', methods=['GET', 'POST'])
@multi_auth.login_required
def modify_event_planner(user_id):
    if not g.current_user.is_admin:
        abort(401)
    user = User.query.get(user_id)
    if request.method == 'GET':
        return render_template('add-update-user.html.j2', user=user,
                               cancel_redirect=url_for('event_planners.list_event_planners'))
    else:
        is_valid = validate_and_save(user, request)
        if is_valid:
            flash("{name} updated".format(name=user.name), "success")
            return redirect(url_for('event_planners.list_event_planners'))
        else:
            return render_template('add-update-user.html.j2', user=user,
                                   cancel_redirect=url_for('event_planners.list_event_planners'))


def validate_and_save(user, request):
    is_valid = True
    user.name = request.form['name']
    user.username = request.form['username']
    if request.form['password']:
        user.set_password(request.form['password'], user.password)
    user.is_admin = 'is_admin' in request.form and request.form['is_admin'] == 'on'
    user.is_active = 'is_active' in request.form and request.form['is_active'] == 'on'
    if user.name is None or len(user.name) == 0:
        flash("Name is required", "error")
        is_valid = False
    if user.username is None or len(user.username) == 0:
        flash("Username is required", "error")
        is_valid = False
    else:
        users_with_username = User.query.filter_by(username=user.username).limit(2).all()

        if len(users_with_username) > 0 and not(
                len(users_with_username) == 1
                and users_with_username[0].id == user.id):
            flash("Username {username} is already taken".format(username=user.username), "error")
            is_valid = False
        # Require password on add
        if len(users_with_username) == 0 and (user.password is None or user.password == ''):
            flash("Password is required", "error")
    if is_valid:
        db.session.add(user)
        db.session.commit()
    return is_valid
