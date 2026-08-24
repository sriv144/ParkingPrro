from flask_smorest import Api


def register_blueprints(api: Api) -> None:
    from parkingpro.api.auth import blueprint as auth_blueprint
    from parkingpro.api.health import blueprint as health_blueprint
    from parkingpro.api.internal import blueprint as internal_blueprint
    from parkingpro.api.lots import blueprint as lots_blueprint
    from parkingpro.api.operator import blueprint as operator_blueprint
    from parkingpro.api.payments import blueprint as payments_blueprint
    from parkingpro.api.reservations import blueprint as reservations_blueprint
    from parkingpro.api.vehicles import blueprint as vehicles_blueprint

    api.register_blueprint(auth_blueprint)
    api.register_blueprint(health_blueprint)
    api.register_blueprint(lots_blueprint)
    api.register_blueprint(vehicles_blueprint)
    api.register_blueprint(reservations_blueprint)
    api.register_blueprint(payments_blueprint)
    api.register_blueprint(operator_blueprint)
    api.register_blueprint(internal_blueprint)
