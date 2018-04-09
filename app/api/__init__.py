from flask import Blueprint
from flask_restful import Api

api = Blueprint('api', __name__)
restful = Api(api)

from . import authentication, posts, users, comments, errors
