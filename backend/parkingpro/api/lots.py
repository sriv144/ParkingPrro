import uuid

from flask_smorest import Blueprint

from parkingpro.extensions import limiter
from parkingpro.schemas import LotSchema, LotSearchSchema, QuoteResponseSchema, QuoteSchema
from parkingpro.services.catalog import create_quote, get_lot, lot_payload, search_lots

blueprint = Blueprint("lots", __name__, url_prefix="/api/v1/lots", description="Parking facilities")


@blueprint.get("")
@blueprint.arguments(LotSearchSchema, location="query")
@blueprint.response(200, LotSchema(many=True))
@limiter.limit("30 per minute")
def list_lots(query):  # type: ignore[no-untyped-def]
    return search_lots(query)


@blueprint.get("/<uuid:lot_id>")
@blueprint.response(200, LotSchema)
def lot_detail(lot_id: uuid.UUID):
    return lot_payload(get_lot(lot_id))


@blueprint.post("/<uuid:lot_id>/quote")
@blueprint.arguments(QuoteSchema)
@blueprint.response(200, QuoteResponseSchema)
def quote(data, lot_id: uuid.UUID):  # type: ignore[no-untyped-def]
    return create_quote(lot_id, data)
