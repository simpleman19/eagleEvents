from flask import Blueprint, request, jsonify, abort, g, Response
from eagleEvents.models.table import Table
from eagleEvents import db
from eagleEvents.auth import multi_auth
from eagleEvents.routes.api import bad_request, validation_error

tables_api_blueprint = Blueprint('tables_api', __name__, url_prefix='/api/table')


@tables_api_blueprint.route('<table_id>', methods=['GET'])
@multi_auth.login_required
def get_table(table_id):
    response = {
        'table': {}
    }
    try:
        table = Table.query.get(table_id)
        if table is not None:
            response['table'] = {
                'id': table.id,
                'number': table.number,
                'seating_capacity': table.seating_capacity,
                'event_id': table.event.id
            }
        else:
            return bad_request('Error finding table with id ' + table_id)
    except Exception:
        return bad_request('Exception thrown finding table with id ' + table_id)      

    return jsonify(response), 200


@tables_api_blueprint.route('', methods=['GET'])
@multi_auth.login_required
def get_tables():
    response = {
        'tables': []
    }
    try:
        tables =  Table.query.all()
        if tables is not None:
            for table in tables:
                response['tables'].append({
                    'id': table.id,
                    'number': table.number,
                    'seating_capacity': table.seating_capacity,
                    'event_id': table.event.id
                })
        else:
            return bad_request('Error getting tables')
    except Exception:
        return bad_request('Exception thrown getting tables')

    return jsonify(response), 200


@tables_api_blueprint.route('<table_id>', methods=['PUT'])
@multi_auth.login_required
def update_table(table_id):
    request_data = request.get_json()
    new_table = {
        'id': table_id,
        'event_id': request_data['event_id'],
        'number': request_data['number'],
        'seating_capacity': request_data['seating_capacity']
    }
    current_company = g.current_user.company
    try:
        table = Table.query.get(table_id)
        if table is not None:
            if float(new_table['number']) and new_table['seating_capacity'] in current_company.table_sizes:
                table.event_id = new_table['event_id']
                table.number = new_table['number']
                table.seating_capacity = new_table['seating_capacity']
                db.session.commit()
            else:
                raise ValueError('value(s) for table not allowed')
        else:
            return bad_request('Error updating table with id ' + table_id)
    except Exception:
        return bad_request('Exception thrown updating table with id ' + table_id)
    
    response = Response("", status = 204)
    return response

    


@tables_api_blueprint.route('/guests', methods=['GET'])
@multi_auth.login_required
def get_guests_for_table():
    table_id = request.args.get('table')
    selected_guest = request.args.get('selGuest')
    response = {
        'guests': [],
        'tables': [],
    }
    if table_id is not None:
        try:
            table = Table.query.filter_by(id=table_id).one_or_none()
            event = table.event
            if table is not None:
                response['tables'] = [{
                    'number': t.number,
                    'id': t.id
                } for t in event.tables]
                response['guests'] = [{
                    'full_name': g.full_name,
                    'id': str(g.id),
                    'first_name': g.first_name,
                    'last_name': g.last_name,
                    'table_id': g.table_id
                } for g in table.guests]
                response['empty_seat'] = table.seating_capacity > len(table.guests)
                return jsonify(response), 200
            else:
                return jsonify({'error': 'Error finding table'}), 404
        # If anything threw an exception (Probably a sql statement)
        except Exception:
            return jsonify({'error': 'Error finding table, exception thrown'}), 404
    else:
        abort(404)


@tables_api_blueprint.route('/prefs', methods=['GET'])
@multi_auth.login_required
def get_prefs_for_table():
    response = {
        'prefs': []
    }
    table1_id = request.args.get('table1')
    table2_id = request.args.get('table2')
    guest1 = request.args.get('guest1')
    guest2 = request.args.get('guest2')
    table1 = Table.query.filter_by(id=table1_id).one_or_none()
    table2 = Table.query.filter_by(id=table2_id).one_or_none()

    for g1 in table1.guests:
        for g2 in table2.guests:
            if str(g1.id) == guest1:
                guest_actual = g1
            elif str(g2.id) == guest1:
                guest_actual = g2
            if g1.likes(g2) or g2.likes(g1):
                if str(g1.id) == guest1 or str(g1.id) == guest2 or str(g2.id) == guest1 or str(g2.id) == guest2:
                    response['prefs'].append({
                        'message': "Notice: " + g1.first_name + " " + g1.last_name + " and "\
                                   + g2.first_name + " " + g2.last_name + " would like to sit together."
                    })
            elif g1.dislikes(g2) or g2.dislikes(g1):
                if str(g1.id) == guest1 or str(g1.id) == guest2 or str(g2.id) == guest1 or str(g2.id) == guest2:
                    response['prefs'].append({
                        'message': "Warning: " + g1.first_name + " " + g1.last_name + " and " \
                                   + g2.first_name + " " + g2.last_name + " should not sit together."
                    })
    for g in table1.guests:
        if guest_actual.id != g.id and (g.likes(guest_actual) or guest_actual.likes(g)):
            response['prefs'].append({
                        'message': "Warning: " + guest_actual.first_name + " " + guest_actual.last_name + " and "\
                                   + g.first_name + " " + g.last_name + " would like to sit together."
                    })            

    return jsonify(response)
