from uuid import UUID

from flask import Blueprint, request, jsonify, abort
from eagleEvents.models import db, Customer
from eagleEvents.auth import multi_auth

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
            return jsonify({'error': 'Error finding customer'}), 404
    except Exception:
        return jsonify({'error': 'Error finding customer, exception thrown'}), 404

    return jsonify(response), 200

