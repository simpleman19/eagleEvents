from flask import Blueprint, request, jsonify, abort
from eagleEvents.models.table import Table
from eagleEvents.auth import multi_auth

tables_api_blueprint = Blueprint('tables_api', __name__, url_prefix='/api/table')


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
    return jsonify(response)
