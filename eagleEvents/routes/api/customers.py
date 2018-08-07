from flask import Blueprint, request, jsonify, abort
from eagleEvents.models import db
from eagleEvents.auth import multi_auth

customers_api_blueprint = Blueprint('customers_api', __name__, url_prefix='/api/customer')
