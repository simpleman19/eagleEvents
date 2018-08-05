from flask import Blueprint, request, jsonify, abort
from eagleEvents.models import db
from eagleEvents.auth import multi_auth

user_api_blueprint = Blueprint('users_api', __name__, url_prefix='/api/user')
