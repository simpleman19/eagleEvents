from flask import jsonify


def bad_request(message):
    return jsonify({'error': message}), 400


def validation_error(errors):
    return jsonify({'error': 'Invalid data', 'errors': errors})

