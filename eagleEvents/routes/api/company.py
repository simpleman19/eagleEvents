from flask import Blueprint, request, jsonify, abort
from eagleEvents.models import db
from eagleEvents.auth import multi_auth

company_api_blueprint = Blueprint('company_api', __name__, url_prefix='/api/company')
