from flask import Blueprint, request, jsonify, abort
from eagleEvents.models.table import Table
from eagleEvents.auth import multi_auth

tables_api_blueprint = Blueprint('tables_api', __name__, url_prefix='/api/table')


@tables_api_blueprint.route('/guests', methods=['GET'])
@multi_auth.login_required
def get_guests_for_table():
    table_id = request.args.get('table')
    response = {
        'guests': []
    }
    if table_id is not None:
        try:
            table = Table.query.filter_by(id=table_id).one_or_none()
            if table is not None:
                response['guests'] = [{
                    'full_name': g.full_name,
                    'id': str(g.id),
                    'first_name': g.first_name,
                    'last_name': g.last_name
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
