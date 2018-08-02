from flask import Blueprint, render_template
from eagleEvents.auth import multi_auth
customers_blueprint = Blueprint('customers', __name__)


@customers_blueprint.route('/listCustomers')
@multi_auth.login_required
def list_customers():
    # TODO List customers
    return render_template('customer.html.j2')


@customers_blueprint.route('/modifyCustomer')
@multi_auth.login_required
def modify_customer():
    # TODO add or modify customer
    return render_template('add-customer.html.j2')

