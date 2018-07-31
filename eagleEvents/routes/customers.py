from flask import Blueprint, redirect, render_template, request, url_for
from eagleEvents import db
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
    customer = Customer.query.get(customer_id)
    if request.method == 'GET':
        return render_template('add-update-customer.html.j2', customer=customer)
    else:
        customer.name = request.form['name']
        customer.email = request.form['email']
        customer.phone_number = request.form['phone']
        db.session.add(customer)
        db.session.commit()
        return redirect(url_for('customers.list_customers'))

