import uuid

from flask_smorest import Blueprint

from parkingpro.schemas import (
    MessageSchema,
    VehicleCreateSchema,
    VehicleSchema,
    VehicleUpdateSchema,
)
from parkingpro.services.catalog import (
    create_vehicle,
    delete_vehicle,
    list_vehicles,
    update_vehicle,
    vehicle_payload,
)
from parkingpro.services.security import current_user

blueprint = Blueprint(
    "vehicles", __name__, url_prefix="/api/v1/vehicles", description="Driver vehicles"
)


@blueprint.get("")
@blueprint.response(200, VehicleSchema(many=True))
def vehicles():
    from flask_jwt_extended import verify_jwt_in_request

    verify_jwt_in_request()
    return list_vehicles(current_user())


@blueprint.post("")
@blueprint.arguments(VehicleCreateSchema)
@blueprint.response(201, VehicleSchema)
def add_vehicle(data):  # type: ignore[no-untyped-def]
    from flask_jwt_extended import verify_jwt_in_request

    verify_jwt_in_request()
    return vehicle_payload(create_vehicle(current_user(), data))


@blueprint.patch("/<uuid:vehicle_id>")
@blueprint.arguments(VehicleUpdateSchema)
@blueprint.response(200, VehicleSchema)
def patch_vehicle(data, vehicle_id: uuid.UUID):  # type: ignore[no-untyped-def]
    from flask_jwt_extended import verify_jwt_in_request

    verify_jwt_in_request()
    return vehicle_payload(update_vehicle(current_user(), vehicle_id, data))


@blueprint.delete("/<uuid:vehicle_id>")
@blueprint.response(200, MessageSchema)
def remove_vehicle(vehicle_id: uuid.UUID):
    from flask_jwt_extended import verify_jwt_in_request

    verify_jwt_in_request()
    delete_vehicle(current_user(), vehicle_id)
    return {"message": "Vehicle deleted."}
