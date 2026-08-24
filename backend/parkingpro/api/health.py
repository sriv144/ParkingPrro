from flask import current_app
from flask_smorest import Blueprint
from redis import Redis
from sqlalchemy import text

from parkingpro.extensions import db

blueprint = Blueprint("health", __name__, url_prefix="/health", description="Service health")


@blueprint.get("/live")
def live():
    return {
        "status": "ok",
        "service": "parkingpro-api",
        "version": current_app.config["API_VERSION"],
    }


@blueprint.get("/ready")
def ready():
    db.session.execute(text("SELECT 1"))
    redis_client = Redis.from_url(
        current_app.config["REDIS_URL"],
        socket_connect_timeout=1,
        socket_timeout=1,
    )
    try:
        redis_client.ping()
    finally:
        redis_client.close()
    return {"status": "ready"}
