from flask import Blueprint, request, jsonify
from functools import wraps
<<<<<<< HEAD
from flask_jwt_extended import jwt_required, get_jwt
=======
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
>>>>>>> 20f5d19e6e8033dcd30bd885ac124933a0f92348
from models import db, ParkingLot, ParkingSpot, User, Reservation

admin_bp = Blueprint('admin', __name__)

<<<<<<< HEAD
# Middleware to check for admin token
=======
>>>>>>> 20f5d19e6e8033dcd30bd885ac124933a0f92348
def admin_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        claims = get_jwt()
        if claims.get('role') != 'admin':
            return jsonify(msg="Admins only"), 403
        return fn(*args, **kwargs)
    return wrapper

<<<<<<< HEAD
# ------------------------- LOT ROUTES -------------------------

=======
>>>>>>> 20f5d19e6e8033dcd30bd885ac124933a0f92348
@admin_bp.route('/lots', methods=['GET'])
@admin_required
def list_lots():
    lots = ParkingLot.query.all()
    result = []
    for lot in lots:
        available = ParkingSpot.query.filter_by(lot_id=lot.id, status='A').count()
        occupied = ParkingSpot.query.filter_by(lot_id=lot.id, status='O').count()
        result.append({
            'id': lot.id,
            'name': lot.prime_location_name,
            'address': lot.address,
            'pin_code': lot.pin_code,
            'price': lot.price,
            'capacity': lot.number_of_spots,
            'available_spots': available,
            'occupied_spots': occupied
        })
    return jsonify(lots=result), 200

<<<<<<< HEAD

=======
>>>>>>> 20f5d19e6e8033dcd30bd885ac124933a0f92348
@admin_bp.route('/lots/<int:lot_id>', methods=['GET'])
@admin_required
def get_lot(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)
    spots = [{'id': s.id, 'status': s.status} for s in lot.spots]
    return jsonify({
        'id': lot.id,
        'name': lot.prime_location_name,
        'address': lot.address,
        'pin_code': lot.pin_code,
        'price': lot.price,
        'capacity': lot.number_of_spots,
        'spots': spots
    }), 200

<<<<<<< HEAD

=======
>>>>>>> 20f5d19e6e8033dcd30bd885ac124933a0f92348
@admin_bp.route('/lots', methods=['POST'])
@admin_required
def create_lot():
    data = request.get_json() or {}
    required = ['prime_location_name', 'address', 'pin_code', 'price', 'number_of_spots']
<<<<<<< HEAD
    if not all(field in data for field in required):
        return jsonify(msg="Missing fields"), 400

=======
    if not all(k in data for k in required):
        return jsonify(msg="Missing fields"), 400
>>>>>>> 20f5d19e6e8033dcd30bd885ac124933a0f92348
    lot = ParkingLot(
        prime_location_name=data['prime_location_name'],
        address=data['address'],
        pin_code=data['pin_code'],
        price=data['price'],
        number_of_spots=data['number_of_spots']
    )
    db.session.add(lot)
<<<<<<< HEAD
    db.session.flush()  # Get lot.id before commit

    # Create parking spots
    spots = [ParkingSpot(lot_id=lot.id) for _ in range(lot.number_of_spots)]
    db.session.add_all(spots)
    db.session.commit()

    return jsonify(msg="Lot created", lot_id=lot.id), 201


=======
    db.session.flush()
    spots = [ParkingSpot(lot_id=lot.id) for _ in range(lot.number_of_spots)]
    db.session.add_all(spots)
    db.session.commit()
    return jsonify(msg="Lot created", lot_id=lot.id), 201

>>>>>>> 20f5d19e6e8033dcd30bd885ac124933a0f92348
@admin_bp.route('/lots/<int:lot_id>', methods=['PUT'])
@admin_required
def update_lot(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)
    data = request.get_json() or {}
<<<<<<< HEAD

    # Update lot details
    for field in ['prime_location_name', 'address', 'pin_code', 'price']:
        if field in data:
            setattr(lot, field, data[field])

    # Handle capacity change
    if 'number_of_spots' in data:
        new_cap = data['number_of_spots']
        cur_cap = lot.number_of_spots

        if new_cap > cur_cap:
            # Add new spots
            for _ in range(new_cap - cur_cap):
                db.session.add(ParkingSpot(lot_id=lot.id))

        elif new_cap < cur_cap:
            # Remove available spots only
            removable = ParkingSpot.query.filter_by(lot_id=lot.id, status='A').limit(cur_cap - new_cap).all()
            if len(removable) < (cur_cap - new_cap):
                return jsonify(msg="Cannot reduce below number of occupied spots"), 400
            for s in removable:
                db.session.delete(s)

        lot.number_of_spots = new_cap

    db.session.commit()
    return jsonify(msg="Lot updated"), 200


=======
    for field in ['prime_location_name', 'address', 'pin_code', 'price']:
        if field in data:
            setattr(lot, field, data[field])
    if 'number_of_spots' in data:
        new_cap = data['number_of_spots']
        cur_cap = lot.number_of_spots
        if new_cap > cur_cap:
            for _ in range(new_cap - cur_cap):
                db.session.add(ParkingSpot(lot_id=lot.id))
        elif new_cap < cur_cap:
            to_remove = ParkingSpot.query.filter_by(lot_id=lot.id, status='A')\
                                         .limit(cur_cap - new_cap).all()
            if len(to_remove) < (cur_cap - new_cap):
                return jsonify(msg="Cannot reduce below occupied"), 400
            for spot in to_remove:
                db.session.delete(spot)
        lot.number_of_spots = new_cap
    db.session.commit()
    return jsonify(msg="Lot updated"), 200

>>>>>>> 20f5d19e6e8033dcd30bd885ac124933a0f92348
@admin_bp.route('/lots/<int:lot_id>', methods=['DELETE'])
@admin_required
def delete_lot(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)
<<<<<<< HEAD
    occupied_count = ParkingSpot.query.filter_by(lot_id=lot.id, status='O').count()

    if occupied_count > 0:
        return jsonify(msg="Cannot delete lot with occupied spots"), 400

=======
    occ = ParkingSpot.query.filter_by(lot_id=lot.id, status='O').count()
    if occ > 0:
        return jsonify(msg="Cannot delete lot with occupied spots"), 400
>>>>>>> 20f5d19e6e8033dcd30bd885ac124933a0f92348
    db.session.delete(lot)
    db.session.commit()
    return jsonify(msg="Lot deleted"), 200

<<<<<<< HEAD
# ------------------------- USER ROUTES -------------------------

=======
>>>>>>> 20f5d19e6e8033dcd30bd885ac124933a0f92348
@admin_bp.route('/users', methods=['GET'])
@admin_required
def list_users():
    users = User.query.all()
<<<<<<< HEAD
    result = []
    for u in users:
        active_res = Reservation.query.filter_by(user_id=u.id, leaving_timestamp=None).all()
        result.append({
            'id': u.id,
            'username': u.username,
            'email': u.email,
            'phone_number': u.phone_number,
            'vehicle_number': u.vehicle_number,
            'vehicle_type': u.vehicle_type,
            'gender': u.gender,
            'address': u.address,
            'is_admin': u.is_admin,
            'active_spot_ids': [r.spot_id for r in active_res]
        })
    return jsonify(users=result), 200
=======
    out = []
    for u in users:
        active = Reservation.query.filter_by(user_id=u.id, leaving_timestamp=None).all()
        out.append({
            'id': u.id,
            'username': u.username,
            'email': u.email,
            'active_spot_ids': [r.spot_id for r in active]
        })
    return jsonify(users=out), 200
>>>>>>> 20f5d19e6e8033dcd30bd885ac124933a0f92348
