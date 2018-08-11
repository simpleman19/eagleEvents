from flask import Blueprint, request, jsonify, abort, g, flash
from eagleEvents.models.guest import Guest
from eagleEvents.models.table import Table
from eagleEvents.models import db, Event, User, Customer
from eagleEvents.auth import multi_auth
from eagleEvents.routes.api import bad_request, validation_error

events_api_blueprint = Blueprint('events_api', __name__, url_prefix='/api/event')


@events_api_blueprint.route('', methods=['GET'])
@multi_auth.login_required
def get_events():
    planner_id = request.args.get('planner')
    customer_id = request.args.get('customer')

    response = {
        'events': []
    }

    if planner_id:
        try:
            planner = User.query.get(planner_id)
            if planner is None:
                return bad_request('Error finding planner')
        except Exception:
            return bad_request('Error finding planner, exception thrown')

    if customer_id:
        try:
            customer = Customer.query.get(customer_id)
            if customer is None:
                return bad_request('Error finding customer')
        except Exception:
            return bad_request('Error finding customer, exception thrown')

    try:
        params = {
            'company': g.current_user.company
        }
        if planner_id is not None:
            params['planner'] = planner
        if customer_id is not None:
            params['customer'] = customer
        events = Event.query.filter_by(**params).all()

        if events is not None:
            for event in events:
                response['events'].append({
                    'id': event.id,
                    'name': event.name,
                    'venue': event.venue,
                    'tableSize': event.table_size.size,
                    'time': event.time.isoformat(),
                    'totalExpectedGuests': len(event._guests),
                    'percentExtraSeats': event.percent_extra_seats,
                    'customerId': event.customer.id,
                    'plannerId': (event.planner.id if event.planner is not None else None),
                    'isDone': event.is_done
                })
        else:
            return bad_request('Error getting events')
    except Exception:
        return bad_request('Error getting event, exception thrown')

    return jsonify(response), 200


@events_api_blueprint.route('<event_id>', methods=['GET'])
@multi_auth.login_required
def get_event(event_id):
    response = {
        'event': {}
    }
    try:
        event = Event.query.get(event_id)
        if event is not None:
            response['event'] = {
                'id': event.id,
                'name': event.name,
                'venue': event.venue,
                'tableSize': event.table_size.size,
                'time': event.time.isoformat(),
                'totalExpectedGuests': len(event._guests),
                'percentExtraSeats': event.percent_extra_seats,
                'customerId': event.customer.id,
                'plannerId': event.planner.id,
                'isDone': event.is_done,
                'guestIds': [g.id for g in event._guests]
            }
        else:
            return bad_request('Error finding event')
    except Exception:
        return bad_request('Error finding event, exception thrown')

    return jsonify(response), 200


@events_api_blueprint.route('', methods=['POST'])
@events_api_blueprint.route('<event_id>', methods=['PUT'])
@multi_auth.login_required
def add_update_event(event_id=None):
    try:
        event_data = request.json
    except Exception:
        return bad_request('Needs json')

    if 'id' in event_data and request.method == 'POST':
        return bad_request('Cannot specify id')

    if request.method == 'POST':
        event = Event(Customer(g.current_user.company))
    else:
        try:
            event = Event.query.get(event_id)
            if event is None:
                return bad_request('Error finding event')
        except Exception:
            return bad_request('Error finding event, exception thrown')

    errors = Event.validate_and_save(event, event_data)

    if len(errors) > 0:
        return validation_error(errors)

    response = jsonify({'id': event.id})

    if request.method == 'POST':
        return response, 201
    else:
        return response, 200


@events_api_blueprint.route('<event_id>/generateSeatingChart', methods=['PUT'])
@multi_auth.login_required
def generate_seating_chart(event_id):
    response = {
        'acknowledged': False
    }
    try:
        event = Event.query.get(event_id)
        if event is not None:
            event.generate_seating_chart()
            response['acknowledged'] = True
        else:
            return bad_request('Error finding event')
    except Exception:
        return bad_request('Error finding event, exception thrown')

    return jsonify(response), 200


"""
    API endpoint to change guest seat
    Method: POST

    Allows user to manually move guests between tables and even swap guests if needed

    Expected JSON to move guest to open seat:
    {
        'selectedGuest' : '<UUID>'     # REQUIRED, This is the guest initially selected to move
        'destinationTable' : '<UUID>'  # REQUIRED, This is the table that the selected guest is moving to
    }

    Expected JSON to swap guests
    {
        'selectedGuest' : '<UUID>'     # REQUIRED, This is the guest initially selected to move
        'otherGuest' : '<UUID>'     # REQUIRED, This is used if swapping 2 guests
    }

    Response JSON:
    {
        'error' : '<This field will contain any error messages to show user>'
        'success' : '<This field will contain any success messages to show user>'
    }
"""


@events_api_blueprint.route('/changeSeat', methods=['POST'])
@multi_auth.login_required
def change_seats():
    response = {
        'error': '',
        'success': ''
    }
    return_code = 500
    json = request.json
    # Validate JSON
    if not json:
        response['error'] = "Error, invalid json in request"
        return jsonify(response), 400
    if not (('selectedGuest' in json and 'destinationTable' in json) or (
            'selectedGuest' in json and 'otherGuest' in json)):
        response['error'] = "Missing required fields in request JSON"
        return jsonify(response), 400
    try:
        # Find guest
        sel_guest: Guest = Guest.query.filter_by(id=json['selectedGuest']).one_or_none()
        # Find table if not swapping
        if 'otherGuest' not in json:
            other_guest = None
            dest_table: Table = Table.query.filter_by(id=json['destinationTable']).one_or_none()
        # Find other guests and get table from other guest
        else:
            other_guest: Guest = Guest.query.filter_by(id=json['otherGuest']).one_or_none()
            # Ensure other guest is found before trying to get table
            if other_guest:
                dest_table = other_guest.assigned_table
            else:
                dest_table = None  # This will break next if statement if table or guest not found
        # Ensure everything was found in database
        if sel_guest and dest_table and (other_guest or 'otherGuest' not in json):
            # Ensure guests and tables are all part of the same event
            if sel_guest.event_id != dest_table.event_id or (
                    other_guest and sel_guest.event_id != other_guest.event_id):
                response['error'] = "Guests and tables are not part of the same event"
                return_code = 400
                return jsonify(response), return_code
            if sel_guest.event.company_id != g.current_user.company.id:
                response['error'] = "You are not authorized to alter an event from another company"
                return_code = 401
                return jsonify(response), return_code
            # If swapping then move other guest
            if other_guest:
                other_guest.assigned_table = sel_guest.assigned_table

            # Swap main guests
            sel_guest.assigned_table = dest_table
            db.session.commit()

            # Return message depending on whether it was a swap or not
            if other_guest:
                response['success'] = "Successfully moved {} to table # {} and {} to table # {}" \
                    .format(sel_guest.full_name, dest_table.number, other_guest.full_name,
                            other_guest.assigned_table.number)
            else:
                response['success'] = "Successfully moved {} to table # {}" \
                    .format(sel_guest.full_name, dest_table.number)
            return_code = 200
        else:
            response['error'] = 'Error finding table or a guest'
            return_code = 404
        return jsonify(response), return_code
    # If anything threw an exception (Probably a filter_by statement)
    except Exception:
        response['error'] = 'Error finding table or a guest, exception thrown'
        return jsonify(response), 404


@events_api_blueprint.route('<event_id>', methods=['DELETE'])
@multi_auth.login_required
def delete_event(event_id):
    event = None
    name = ""
    try:
        event = Event.query.get(event_id)
    except Exception:
        return bad_request('Error deleting event, exception thrown')
    if event:
        name = event.name
        db.session.delete(event)
        db.session.commit()
    else:
        return bad_request("Could not find event to delete")
    flash('Successfully deleted event: ' + name)
    return jsonify({'success': "Successfully deleted event: " + name}), 200
