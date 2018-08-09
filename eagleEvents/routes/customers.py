from flask import Blueprint, redirect, render_template, request, url_for, g, flash, abort, jsonify

from eagleEvents import db
from eagleEvents.auth import multi_auth
from eagleEvents.models import Customer
customers_blueprint = Blueprint('customers', __name__)


@customers_blueprint.route('/listCustomers')
@multi_auth.login_required
def list_customers():
    customers = g.current_user.company.customers;
    return render_template('customer.html.j2', customers = customers)


@customers_blueprint.route('/addCustomer', methods=['GET', 'POST'])
@multi_auth.login_required
def add_customer():
    customer = Customer(g.current_user.company)
    if request.method == 'GET':
        return render_template('add-update-customer.html.j2', customer=customer,
                               cancel_redirect=url_for('customers.list_customers'))
    else:
        errors = Customer.validate_and_save(customer, request)
        if len(errors) == 0:
            flash("{name} added".format(name=customer.name), "success")
            return redirect(url_for('customers.list_customers'))
        else:
            for e in errors:
                flash(e, 'error')
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
        errors = Customer.validate_and_save(customer, request.form)
        if len(errors) == 0:
            flash("{name} updated".format(name=customer.name), "error")
            return redirect(url_for('customers.list_customers'))
        else:
            for e in errors:
                flash(e, 'error')
            return render_template('add-update-customer.html.j2', customer=customer,
                                   cancel_redirect=url_for('customers.list_customers'))


@customers_blueprint.route('/deleteCustomer/<id>', methods=['DELETE'])
@multi_auth.login_required
def delete_customer(id):
    customer = None
    name = ""
    try:
        customer = Customer.query.filter_by(id=id, company=g.current_user.company).one_or_none()
    except Exception as e:
        print(e)
        abort(404)
    if customer:
        name = customer.name
        db.session.delete(customer)
        db.session.commit()
    else:
        print("Could not find customer to delete")
        abort(404)
    flash('Successfully deleted customer: ' + name)
    return jsonify({'success': "Successfully deleted customer: " + name}), 200
