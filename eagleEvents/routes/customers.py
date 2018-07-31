from flask import Blueprint, render_template, request
from eagleEvents.auth import multi_auth
from eagleEvents.models import Customer
customers_blueprint = Blueprint('customers', __name__)


@customers_blueprint.route('/listCustomers')
@multi_auth.login_required
def list_customers():
    # TODO List customers
    return render_template('customer.html.j2')


@customers_blueprint.route('/modifyCustomer/<customer_id>', methods=['GET', 'POST'])
@multi_auth.login_required
def modify_customer(customer_id):
    if request.method == 'GET':
        customer = Customer.query.get(customer_id)
        return render_template('add-update-customer.html.j2', customer=customer)
    # TODO add or modify customer

