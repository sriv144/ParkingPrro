import uuid

from flask_smorest import Blueprint

from parkingpro.models import OperationalState, ReservationStatus, Role
from parkingpro.schemas import (
    LotSchema,
    OperatorLotCreateSchema,
    OperatorLotUpdateSchema,
    OverviewSchema,
    ReservationSchema,
    ScanSchema,
    SpotSchema,
    SpotUpdateSchema,
)
from parkingpro.services.catalog import lot_payload
from parkingpro.services.operator import (
    create_operator_lot,
    list_operator_lots,
    list_operator_reservations,
    list_operator_spots,
    overview,
    scan_pass,
    spot_payload,
    transition_reservation,
    update_operator_lot,
    update_operator_spot,
)
from parkingpro.services.reservations import reservation_payload
from parkingpro.services.security import current_user, roles_required

blueprint = Blueprint(
    "operator",
    __name__,
    url_prefix="/api/v1/operator",
    description="Operator console",
)


@blueprint.get("/overview")
@blueprint.response(200, OverviewSchema)
@roles_required(Role.OPERATOR, Role.ADMIN)
def operator_overview():
    return overview(current_user())


@blueprint.get("/lots")
@blueprint.response(200, LotSchema(many=True))
@roles_required(Role.OPERATOR, Role.ADMIN)
def operator_lots():
    return list_operator_lots(current_user())


@blueprint.post("/lots")
@blueprint.arguments(OperatorLotCreateSchema)
@blueprint.response(201, LotSchema)
@roles_required(Role.OPERATOR, Role.ADMIN)
def add_lot(data):  # type: ignore[no-untyped-def]
    return lot_payload(create_operator_lot(current_user(), data))


@blueprint.patch("/lots/<uuid:lot_id>")
@blueprint.arguments(OperatorLotUpdateSchema)
@blueprint.response(200, LotSchema)
@roles_required(Role.OPERATOR, Role.ADMIN)
def patch_lot(data, lot_id: uuid.UUID):  # type: ignore[no-untyped-def]
    return lot_payload(update_operator_lot(current_user(), lot_id, data))


@blueprint.get("/lots/<uuid:lot_id>/spots")
@blueprint.response(200, SpotSchema(many=True))
@roles_required(Role.OPERATOR, Role.ADMIN)
def operator_spots(lot_id: uuid.UUID):
    return list_operator_spots(current_user(), lot_id)


@blueprint.patch("/spots/<uuid:spot_id>")
@blueprint.arguments(SpotUpdateSchema)
@blueprint.response(200, SpotSchema)
@roles_required(Role.OPERATOR, Role.ADMIN)
def patch_spot(data, spot_id: uuid.UUID):  # type: ignore[no-untyped-def]
    return spot_payload(
        update_operator_spot(current_user(), spot_id, OperationalState(data["state"]))
    )


@blueprint.get("/reservations")
@blueprint.response(200, ReservationSchema(many=True))
@roles_required(Role.OPERATOR, Role.ADMIN)
def operator_reservations():
    return list_operator_reservations(current_user())


@blueprint.post("/scan")
@blueprint.arguments(ScanSchema)
@blueprint.response(200, ReservationSchema)
@roles_required(Role.OPERATOR, Role.ADMIN)
def scan(data):  # type: ignore[no-untyped-def]
    return reservation_payload(scan_pass(current_user(), data["qr_payload"]), include_qr=False)


@blueprint.post("/reservations/<uuid:reservation_id>/check-in")
@blueprint.response(200, ReservationSchema)
@roles_required(Role.OPERATOR, Role.ADMIN)
def check_in(reservation_id: uuid.UUID):
    return reservation_payload(
        transition_reservation(current_user(), reservation_id, ReservationStatus.CHECKED_IN),
        include_qr=False,
    )


@blueprint.post("/reservations/<uuid:reservation_id>/check-out")
@blueprint.response(200, ReservationSchema)
@roles_required(Role.OPERATOR, Role.ADMIN)
def check_out(reservation_id: uuid.UUID):
    return reservation_payload(
        transition_reservation(current_user(), reservation_id, ReservationStatus.COMPLETED),
        include_qr=False,
    )
