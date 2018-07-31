from flask import Blueprint, redirect, render_template, request, url_for, g, flash
from eagleEvents import db
from eagleEvents.auth import multi_auth
from eagleEvents.models import Customer
customers_blueprint = Blueprint('customers', __name__)


@customers_blueprint.route('/listCustomers')
@multi_auth.login_required
def list_customers():
    # TODO List customers
    return render_template('customer.html.j2')


@customers_blueprint.route('/addCustomer', methods=['GET', 'POST'])
@multi_auth.login_required
def add_customer():
    customer = Customer(g.current_user.company)
    if request.method == 'GET':
        return render_template('add-update-customer.html.j2', customer=customer,
                               cancel_redirect=url_for('customers.list_customers'))
    else:
        is_valid = validate_and_save(customer, request)
        if is_valid:
            return redirect(url_for('customers.list_customers'))
        else:
            return render_template('add-update-customer.html.j2', customer=customer,
                                   cancel_redirect=url_for('customers.list_customers'))



@customers_blueprint.route('/modifyCustomer/<customer_id>', methods=['GET', 'POST'])
@multi_auth.login_required
def modify_customer(customer_id):
    customer = Customer.query.get(customer_id)
    if request.method == 'GET':
        return render_template('add-update-customer.html.j2', customer=customer,
                               cancel_redirect=url_for('customers.list_customers'))
    else:
        is_valid = validate_and_save(customer, request)
        if is_valid:
            return redirect(url_for('customers.list_customers'))
        else:
            return render_template('add-update-customer.html.j2', customer=customer,
                                   cancel_redirect=url_for('customers.list_customers'))


def validate_and_save(customer, request):
    customer.name = request.form['name']
    customer.email = request.form['email']
    customer.phone_number = request.form['phone']
    if customer.name is None or len(customer.name) == 0:
        flash("Name is required", "error")
        return False
    else:
        db.session.add(customer)
        db.session.commit()
        return True
