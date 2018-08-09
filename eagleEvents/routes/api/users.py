from flask import Blueprint, request, jsonify, abort, g, flash
from eagleEvents.models import db
from eagleEvents.auth import multi_auth
from eagleEvents.models.user import User

user_api_blueprint = Blueprint('users_api', __name__, url_prefix='/api/user')


@user_api_blueprint.route('/users', methods=['GET'])
@multi_auth.login_required
def get_all_users():
    company = g.current_user.company
    response = {
        'users': []
    }
    if company and len(company.users) > 0:
        response['users'] = [{
            'id': u.id,
            'name': u.name,
            'username': u.username,
            'active': u.is_active,
            'admin': u.is_admin
        } for u in company.users]
    else:
        response = {'error': "No Users Found for " + company.name}
    return jsonify(response)


@user_api_blueprint.route('/', methods=['GET', 'POST'])
@multi_auth.login_required
def get_user():
    company = g.current_user.company_id
    userid = request.args.get('userId')
    if company and userid:
        user = User.query.filter_by(company_id=company, id=userid).one_or_none()
        response = {
            'id': user.id,
            'name': user.name,
            'username': user.username,
            'admin': user.is_admin,
            'active': user.is_active
        }
    else:
        response = {
            'id': '',
            'name': request.args.get('name'),
            'username': request.args.get('username'),
            'admin': request.args.get('admin'),
            'active': request.args.get('active')
        }
        print(response)
    return jsonify(response)


@user_api_blueprint.route('/save', methods=['POST'])
@multi_auth.login_required
def validate_and_save_user():
    response = {
        'error': '',
        'success': ''
    }
    return_code = 500
    json = request.json
    # Validate JSON
    if not json:
        response['error'] = "Error, invalid json in request"
        return jsonify(response), 400
    try:
        if len(json['id']) > 0:
            user = User.query.filter_by(company=g.current_user.company, id=json['id']).one_or_none()
        else:
            user = User(g.current_user.company)
        is_valid = True
        user.name = json['name']
        user.username = json['username']
        print(json['password'])
        if json['password']:
            user.set_password(json['password'], user.password)
        user.is_admin = json['admin']
        user.is_active = json['active']
        if user.name is None or len(user.name) == 0:
            flash("Name is required", "error")
            is_valid = False
        if user.username is None or len(user.username) == 0:
            flash("Username is required", "error")
            is_valid = False
        else:
            users_with_username = User.query.filter_by(username=user.username).limit(2).all()

            if len(users_with_username) > 0 and not (
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
            response['success'] = "User saved to database"
            return_code = 200
            flash("User Modifications Complete")
        return jsonify(response), return_code
    # If anything threw an exception (Probably a filter_by statement
    except Exception:
        response['error'] = 'Error storing user, exception thrown'
        return jsonify(response), 404
