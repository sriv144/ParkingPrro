from marshmallow import RAISE, Schema, ValidationError, fields, validate, validates_schema


class StrictSchema(Schema):
    class Meta:
        unknown = RAISE


class PublicRegisterSchema(StrictSchema):
    email = fields.Email(required=True)
    password = fields.String(
        required=True, load_only=True, validate=validate.Length(min=10, max=128)
    )
    full_name = fields.String(required=True, validate=validate.Length(min=2, max=120))
    phone = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=24))


class LoginSchema(StrictSchema):
    email = fields.Email(required=True)
    password = fields.String(
        required=True, load_only=True, validate=validate.Length(min=1, max=128)
    )
    client_type = fields.String(required=True, validate=validate.OneOf(["web", "mobile"]))
    device_name = fields.String(load_default="unknown", validate=validate.Length(max=120))


class RefreshSchema(StrictSchema):
    client_type = fields.String(required=True, validate=validate.OneOf(["web", "mobile"]))
    refresh_token = fields.String(load_default=None, allow_none=True, load_only=True)


class AuthResponseSchema(Schema):
    access_token = fields.String(required=True)
    refresh_token = fields.String(allow_none=True)
    csrf_token = fields.String(allow_none=True)
    expires_in = fields.Integer(required=True)
    user = fields.Dict(required=True)


class MessageSchema(Schema):
    message = fields.String(required=True)


class UserSchema(Schema):
    id = fields.UUID(required=True)
    email = fields.Email(required=True)
    full_name = fields.String(required=True)
    phone = fields.String(allow_none=True)
    role = fields.String(required=True)


class PushTokenSchema(StrictSchema):
    token = fields.String(required=True, validate=validate.Length(min=20, max=255))
    platform = fields.String(required=True, validate=validate.OneOf(["android", "ios"]))


class VehicleCreateSchema(StrictSchema):
    registration_number = fields.String(required=True, validate=validate.Length(min=4, max=20))
    label = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=60))
    vehicle_type = fields.String(
        required=True, validate=validate.OneOf(["car", "bike", "ev", "accessible"])
    )


class VehicleUpdateSchema(StrictSchema):
    registration_number = fields.String(validate=validate.Length(min=4, max=20))
    label = fields.String(allow_none=True, validate=validate.Length(max=60))
    vehicle_type = fields.String(validate=validate.OneOf(["car", "bike", "ev", "accessible"]))


class VehicleSchema(Schema):
    id = fields.UUID(required=True)
    registration_number = fields.String(required=True)
    label = fields.String(allow_none=True)
    vehicle_type = fields.String(required=True)


class LotSearchSchema(StrictSchema):
    latitude = fields.Float(load_default=12.9716, validate=validate.Range(min=-90, max=90))
    longitude = fields.Float(load_default=77.5946, validate=validate.Range(min=-180, max=180))
    radius_m = fields.Integer(load_default=10_000, validate=validate.Range(min=250, max=50_000))
    starts_at = fields.AwareDateTime(load_default=None, allow_none=True)
    ends_at = fields.AwareDateTime(load_default=None, allow_none=True)
    spot_type = fields.String(
        load_default=None,
        allow_none=True,
        validate=validate.OneOf(["car", "bike", "ev", "accessible"]),
    )

    @validates_schema
    def validate_window(self, data, **kwargs):  # type: ignore[no-untyped-def]
        start, end = data.get("starts_at"), data.get("ends_at")
        if bool(start) != bool(end):
            raise ValidationError("starts_at and ends_at must be provided together.")
        if start and end and end <= start:
            raise ValidationError("ends_at must be after starts_at.")


class LotSchema(Schema):
    id = fields.UUID(required=True)
    name = fields.String(required=True)
    address = fields.String(required=True)
    latitude = fields.Float(required=True)
    longitude = fields.Float(required=True)
    distance_m = fields.Float(allow_none=True)
    timezone = fields.String(required=True)
    opens_at = fields.String(required=True)
    closes_at = fields.String(required=True)
    base_rate_paise = fields.Integer(required=True)
    state = fields.String(required=True)
    total_spots = fields.Integer(required=True)
    available_spots = fields.Integer(required=True)


class QuoteSchema(StrictSchema):
    starts_at = fields.AwareDateTime(required=True)
    ends_at = fields.AwareDateTime(required=True)
    spot_type = fields.String(
        required=True, validate=validate.OneOf(["car", "bike", "ev", "accessible"])
    )

    @validates_schema
    def validate_window(self, data, **kwargs):  # type: ignore[no-untyped-def]
        if data["ends_at"] <= data["starts_at"]:
            raise ValidationError("ends_at must be after starts_at.")


class QuoteResponseSchema(Schema):
    lot_id = fields.UUID(required=True)
    starts_at = fields.AwareDateTime(required=True)
    ends_at = fields.AwareDateTime(required=True)
    duration_minutes = fields.Integer(required=True)
    amount_paise = fields.Integer(required=True)
    currency = fields.String(required=True)
    available_spots = fields.Integer(required=True)


class ReservationCreateSchema(QuoteSchema):
    lot_id = fields.UUID(required=True)
    vehicle_id = fields.UUID(required=True)


class ReservationSchema(Schema):
    id = fields.UUID(required=True)
    lot_id = fields.UUID(required=True)
    lot_name = fields.String(required=True)
    spot_code = fields.String(required=True)
    vehicle_id = fields.UUID(required=True)
    registration_number = fields.String(required=True)
    starts_at = fields.AwareDateTime(required=True)
    ends_at = fields.AwareDateTime(required=True)
    quoted_amount_paise = fields.Integer(required=True)
    status = fields.String(required=True)
    hold_expires_at = fields.AwareDateTime(allow_none=True)
    qr_payload = fields.String(allow_none=True)


class PaymentOrderSchema(Schema):
    order_id = fields.String(required=True)
    key_id = fields.String(required=True)
    amount_paise = fields.Integer(required=True)
    currency = fields.String(required=True)
    reservation_id = fields.UUID(required=True)


class PaymentVerifySchema(StrictSchema):
    razorpay_order_id = fields.String(required=True, validate=validate.Length(max=120))
    razorpay_payment_id = fields.String(required=True, validate=validate.Length(max=120))
    razorpay_signature = fields.String(required=True, validate=validate.Length(max=256))


class ScanSchema(StrictSchema):
    qr_payload = fields.String(required=True, validate=validate.Length(min=20, max=2048))


class OperatorLotCreateSchema(StrictSchema):
    name = fields.String(required=True, validate=validate.Length(min=2, max=160))
    address = fields.String(required=True, validate=validate.Length(min=4, max=320))
    latitude = fields.Float(required=True, validate=validate.Range(min=-90, max=90))
    longitude = fields.Float(required=True, validate=validate.Range(min=-180, max=180))
    opens_at = fields.String(
        load_default="00:00", validate=validate.Regexp(r"^(?:[01]\d|2[0-3]):[0-5]\d$")
    )
    closes_at = fields.String(
        load_default="23:59", validate=validate.Regexp(r"^(?:[01]\d|2[0-3]):[0-5]\d$")
    )
    base_rate_paise = fields.Integer(required=True, validate=validate.Range(min=1, max=1_000_000))
    capacity = fields.Integer(load_default=20, validate=validate.Range(min=1, max=1000))


class OperatorLotUpdateSchema(StrictSchema):
    name = fields.String(validate=validate.Length(min=2, max=160))
    address = fields.String(validate=validate.Length(min=4, max=320))
    opens_at = fields.String(validate=validate.Regexp(r"^(?:[01]\d|2[0-3]):[0-5]\d$"))
    closes_at = fields.String(validate=validate.Regexp(r"^(?:[01]\d|2[0-3]):[0-5]\d$"))
    base_rate_paise = fields.Integer(validate=validate.Range(min=1, max=1_000_000))
    state = fields.String(validate=validate.OneOf(["active", "out_of_service"]))


class SpotUpdateSchema(StrictSchema):
    state = fields.String(required=True, validate=validate.OneOf(["active", "out_of_service"]))


class SpotSchema(Schema):
    id = fields.UUID(required=True)
    lot_id = fields.UUID(required=True)
    code = fields.String(required=True)
    spot_type = fields.String(required=True)
    state = fields.String(required=True)


class OverviewSchema(Schema):
    occupied_spots = fields.Integer(required=True)
    total_spots = fields.Integer(required=True)
    occupancy_percent = fields.Float(required=True)
    active_reservations = fields.Integer(required=True)
    revenue_today_paise = fields.Integer(required=True)
    completed_today = fields.Integer(required=True)


class HealthSchema(Schema):
    status = fields.String(required=True)
