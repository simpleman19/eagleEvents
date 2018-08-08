from flask import Blueprint, request, jsonify, abort, g
from eagleEvents.models import db
from eagleEvents.auth import multi_auth

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
