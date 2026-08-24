from __future__ import annotations

import os
import uuid

import click
from flask.cli import with_appcontext
from geoalchemy2.elements import WKTElement
from werkzeug.security import generate_password_hash

from parkingpro.extensions import db
from parkingpro.models import OperatorLot, ParkingLot, ParkingSpot, Role, SpotType, User, Vehicle


@click.command("create-operator")
@click.option("--email", prompt=True)
@click.option("--full-name", prompt=True)
@click.password_option()
@click.option("--assign-all/--no-assign-all", default=True, help="Assign all existing facilities.")
@with_appcontext
def create_operator(email: str, full_name: str, password: str, assign_all: bool) -> None:
    normalized = email.strip().lower()
    if db.session.scalar(db.select(User).where(User.email == normalized)):
        raise click.ClickException("An account with that email already exists.")
    operator = User(
        email=normalized,
        full_name=full_name.strip(),
        password_hash=generate_password_hash(password),
        role=Role.OPERATOR,
    )
    db.session.add(operator)
    db.session.flush()
    if assign_all:
        for lot_id in db.session.scalars(db.select(ParkingLot.id)):
            db.session.add(OperatorLot(operator_id=operator.id, lot_id=lot_id))
    db.session.commit()
    click.echo("Operator created.")


DEMO_LOTS = [
    ("Marina Central", "12 MG Road, Bengaluru", 12.9756, 77.6068, 6000, 24),
    ("Indiranagar Metro Parking", "CMH Road, Indiranagar", 12.9784, 77.6408, 5000, 20),
    ("Orion East Gate", "Dr Rajkumar Road, Rajajinagar", 13.0112, 77.5550, 7000, 18),
    ("UB City Parking", "Vittal Mallya Road, Bengaluru", 12.9716, 77.5962, 9000, 30),
    ("Manyata Tech Park", "Nagavara, Bengaluru", 13.0469, 77.6202, 4500, 28),
]
DEMO_NAMESPACE = uuid.UUID("371bf9ca-9fc6-4cc8-9b3d-a26377f0d625")


@click.command("seed-demo")
@with_appcontext
def seed_demo() -> None:
    created = 0
    for name, address, lat, lng, rate, capacity in DEMO_LOTS:
        lot_id = uuid.uuid5(DEMO_NAMESPACE, f"lot:{name}")
        if db.session.get(ParkingLot, lot_id):
            continue
        lot = ParkingLot(
            id=lot_id,
            name=name,
            address=address,
            location=WKTElement(f"POINT({lng} {lat})", srid=4326),
            base_rate_paise=rate,
        )
        db.session.add(lot)
        db.session.flush()
        for number in range(1, capacity + 1):
            if number % 12 == 0:
                spot_type = SpotType.ACCESSIBLE
            elif number % 10 == 0:
                spot_type = SpotType.EV
            elif number % 6 == 0:
                spot_type = SpotType.BIKE
            else:
                spot_type = SpotType.CAR
            db.session.add(
                ParkingSpot(
                    id=uuid.uuid5(DEMO_NAMESPACE, f"spot:{name}:{number}"),
                    lot_id=lot.id,
                    code=f"A-{number:02d}",
                    spot_type=spot_type,
                )
            )
        created += 1
    _seed_demo_users()
    db.session.commit()
    click.echo(f"Demo seed complete; created {created} synthetic Bengaluru facilities.")


def _seed_demo_users() -> None:
    driver_email = os.getenv("DEMO_DRIVER_EMAIL", "").strip().lower()
    driver_password = os.getenv("DEMO_DRIVER_PASSWORD", "")
    operator_email = os.getenv("DEMO_OPERATOR_EMAIL", "").strip().lower()
    operator_password = os.getenv("DEMO_OPERATOR_PASSWORD", "")
    if not all((driver_email, driver_password, operator_email, operator_password)):
        click.echo("Demo user credentials are unset; facilities were seeded without accounts.")
        return
    driver = db.session.scalar(db.select(User).where(User.email == driver_email))
    if not driver:
        driver = User(
            id=uuid.uuid5(DEMO_NAMESPACE, f"user:{driver_email}"),
            email=driver_email,
            full_name="Demo Driver",
            password_hash=generate_password_hash(driver_password),
            role=Role.DRIVER,
        )
        db.session.add(driver)
        db.session.flush()
        db.session.add(
            Vehicle(
                id=uuid.uuid5(DEMO_NAMESPACE, f"vehicle:{driver_email}"),
                owner_id=driver.id,
                registration_number="KA01AB1234",
                label="Demo car",
                vehicle_type=SpotType.CAR,
            )
        )
    operator = db.session.scalar(db.select(User).where(User.email == operator_email))
    if not operator:
        operator = User(
            id=uuid.uuid5(DEMO_NAMESPACE, f"user:{operator_email}"),
            email=operator_email,
            full_name="Demo Operator",
            password_hash=generate_password_hash(operator_password),
            role=Role.OPERATOR,
        )
        db.session.add(operator)
        db.session.flush()
    assigned = set(
        db.session.scalars(
            db.select(OperatorLot.lot_id).where(OperatorLot.operator_id == operator.id)
        )
    )
    for lot_id in db.session.scalars(db.select(ParkingLot.id)):
        if lot_id not in assigned:
            db.session.add(OperatorLot(operator_id=operator.id, lot_id=lot_id))
