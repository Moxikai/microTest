from flask import Blueprint
auth = Blueprint('auth',__name__)

from . import errors,views,forms