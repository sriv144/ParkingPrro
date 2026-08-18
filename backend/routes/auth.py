from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from models import db, User, Admin

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}

    if User.query.filter_by(username=data.get('username')).first():
        return jsonify(msg="Username already taken"), 409
    if User.query.filter_by(email=data.get('email')).first():
        return jsonify(msg="Email already in use"), 409

    user = User(
        username=data['username'],
        email=data['email'],
        password_hash=generate_password_hash(data['password']),
        is_admin=data.get('is_admin', False),
        phone_number=data.get('phone_number'),
        vehicle_number=data.get('vehicle_number'),
        vehicle_type=data.get('vehicle_type'),
        gender=data.get('gender'),
        address=data.get('address')
    )

    db.session.add(user)
    db.session.commit()
    return jsonify(msg="User registered successfully"), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    user = User.query.filter_by(email=data.get('email')).first()
    if not user or not check_password_hash(user.password_hash, data.get('password')):
        return jsonify(msg="Bad username or password"), 401

    token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": "admin" if user.is_admin else "user"}
    )
    return jsonify(access_token=token), 200

@auth_bp.route('/admin/login', methods=['POST'])
def admin_login():
    data = request.get_json() or {}
    admin = Admin.query.filter_by(username=data.get('username')).first()
    if not admin or not check_password_hash(admin.password_hash, data.get('password')):
        return jsonify(msg="Invalid admin credentials"), 401

    token = create_access_token(
        identity=str(admin.id),
        additional_claims={"role": "admin"}
    )
    return jsonify(access_token=token), 200
