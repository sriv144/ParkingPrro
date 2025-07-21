from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Admin(db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

class User(db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(64), unique=True, nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin      = db.Column(db.Boolean, default=False)  # ✅ Add this line
    reservations  = db.relationship('Reservation', back_populates='user')
    phone_number = db.Column(db.String(20))
    vehicle_number = db.Column(db.String(20))
    vehicle_type = db.Column(db.String(20))  # 2-wheeler / 4-wheeler
    gender = db.Column(db.String(10))
    address = db.Column(db.String(255))




class ParkingLot(db.Model):
    id                  = db.Column(db.Integer, primary_key=True)
    prime_location_name = db.Column(db.String(128), nullable=False)
    price               = db.Column(db.Float, nullable=False)
    address             = db.Column(db.String(256))
    pin_code            = db.Column(db.String(20))
    number_of_spots     = db.Column(db.Integer, nullable=False)
    spots               = db.relationship('ParkingSpot', back_populates='lot', cascade='all, delete-orphan')

class ParkingSpot(db.Model):
    id       = db.Column(db.Integer, primary_key=True)
    lot_id   = db.Column(db.Integer, db.ForeignKey('parking_lot.id'), nullable=False)
    status   = db.Column(db.String(1), default='A')  # A=Available, O=Occupied
    lot      = db.relationship('ParkingLot', back_populates='spots')
    reservations = db.relationship('Reservation', back_populates='spot')

class Reservation(db.Model):
    id                = db.Column(db.Integer, primary_key=True)
    spot_id           = db.Column(db.Integer, db.ForeignKey('parking_spot.id'), nullable=False)
    user_id           = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    parking_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    leaving_timestamp = db.Column(db.DateTime)
    parking_cost      = db.Column(db.Float)
    spot              = db.relationship('ParkingSpot', back_populates='reservations')
    user              = db.relationship('User', back_populates='reservations')
