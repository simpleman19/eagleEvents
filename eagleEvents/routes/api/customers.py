from uuid import UUID

from flask import Blueprint, request, jsonify, abort, flash, g
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
@customers_api_blueprint.route('<customer_id>', methods=['PUT'])
@multi_auth.login_required
def add_update_customer(customer_id=None):
    try:
        customer_data = request.json
    except Exception:
        return bad_request('Needs json')

    if 'id' in customer_data and request.method == 'POST':
        return bad_request('Cannot specify id')

    if 'number' in customer_data:
        return bad_request('Cannot specify number')

    try:
        company = Company.query.get(g.current_user.company)
        if company is None:
            return bad_request('Error finding company')
    except Exception:
        return bad_request('Error finding company, exception thrown')

    if request.method == 'POST':
        customer = Customer(company)
    else:
        try:
            customer = Customer.query.get(customer_id)
            if customer is None:
                return bad_request('Error finding customer')
        except Exception:
            return bad_request('Error finding customer, exception thrown')

    errors = Customer.validate_and_save(customer, customer_data)

    if len(errors) > 0:
        return validation_error(errors)

    response = jsonify({'id': customer.id, 'number': customer.number})

    if request.method == 'POST':
        return response, 201
    else:
        return response, 200


@customers_api_blueprint.route('<customer_id>', methods=['DELETE'])
@multi_auth.login_required
def delete_customer(customer_id):
    customer = None
    name = ""
    try:
        customer = Customer.query.get(customer_id)
    except Exception as e:
        return bad_request(e)
    if customer:
        name = customer.name
        db.session.delete(customer)
        db.session.commit()
    else:
        return bad_request("Could not find customer to delete")
    flash('Successfully deleted customer: ' + name)
    return jsonify({'success': "Successfully deleted customer: " + name}), 200
