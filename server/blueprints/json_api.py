from app_service_server import get_all_sensors, get_last_sensor_data, get_folder_uncompleted
from flask import Blueprint, jsonify


bp = Blueprint("api", __name__)


@bp.route("/show-data/.json")
def show_data():
    return jsonify(get_all_sensors())


# TODO: ajustar rota e seu método
@bp.route("/last-sensor-data/<sensor>/.json")
def last_sensor_data(sensor):
    return jsonify(get_last_sensor_data(sensor))


@bp.route("/uncompleted-simulation/.json")
def uncompleted_simulation():
    data = {"folder": None}
    folder_uncompleted = get_folder_uncompleted()
    if len(folder_uncompleted) != 0:
        data["folder"] = folder_uncompleted[0][0]
    return jsonify(data)


def create_bp(app):
    app.register_blueprint(bp)
