from flask import request, jsonify
from . import main
from app import db
from ..models import User


@main.route('/login', methods=['POST', ])
def login():
    email = request.json.get('email')
    print(email)
    password = request.json.get('password')
    print(password)
    user = User.query.filter_by(email=email).first()
    if user:
        if user.verify_password(password):
            return jsonify({
                'login': True
            })
    return jsonify({
        'login': False
    })
