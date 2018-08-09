from uuid import UUID

from flask import Blueprint, request, jsonify, abort
from eagleEvents.models import db, Customer, Company
from eagleEvents.auth import multi_auth
from eagleEvents.routes.api import bad_request, validation_error

customers_api_blueprint = Blueprint('customers_api', __name__, url_prefix='/api/customer')

@customers_api_blueprint.route('<customer_id>', methods=['GET'])
@multi_auth.login_required
def get_customer(customer_id):
    response = {
        'customer': {}
    }
    try:
        customer = Customer.query.get(customer_id)
        if customer is not None:
            response['customer'] = {
                'id': customer.id,
                'number': customer.number,
                'name': customer.name,
                'phoneNumber': customer.phone_number,
                'email': customer.email,
                'eventIds': [e.id for e in customer.events],
                'companyId': customer.company_id
            }
        else:
            return bad_request('Error finding customer')
    except Exception:
        return bad_request('Error finding customer, exception thrown')

    return jsonify(response), 200

@customers_api_blueprint.route('', methods=['POST'])
@multi_auth.login_required
def post_customer():
    try:
        customer_data = request.json
    except Exception:
        return bad_request('Needs json')

    if 'id' in customer_data:
        return bad_request('Cannot specify id')

    if 'number' in customer_data:
        return bad_request('Cannot specify number')

    if not('companyId' in customer_data):
        return bad_request('Need companyId')

    try:
        company = Company.query.get(customer_data['companyId'])
        if company is None:
            return bad_request('Error finding company')
    except Exception:
        return bad_request('Error finding company, exception thrown')

    customer = Customer(company)
    errors = Customer.validate_and_save(customer, customer_data)

    if len(errors) > 0:
        return validation_error(errors)

    return jsonify({'id': customer.id, 'number': customer.number}), 200
