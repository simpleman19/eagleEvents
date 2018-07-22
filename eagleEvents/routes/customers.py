from flask import Blueprint, render_template

customers_blueprint = Blueprint('customers', __name__)


@customers_blueprint.route('/listCustomers')
def list_customers():
    # TODO List customers
    return render_template('test.html.j2')


@customers_blueprint.route('/modifyCustomer')
def modify_customer():
    # TODO add or modify customer
    return render_template('test.html.j2')

