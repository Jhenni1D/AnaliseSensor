from app_service_server import get_all_folders, get_folder_uncompleted
from flask import Blueprint, jsonify


bp = Blueprint("api", __name__)


@bp.route("/show-data/.json")
def show_data():
    return jsonify(get_all_folders())


# TODO: ajustar rota e seu método
@bp.route("/last-simulation-data/.json")
def last_sensor_data():
    return jsonify(get_all_folders()[-1])


@bp.route("/uncompleted-simulation/.json")
def uncompleted_simulation():
    data = {"folder": None}
    folder_uncompleted = get_folder_uncompleted()
    if len(folder_uncompleted) != 0:
        data["folder"] = folder_uncompleted[0][0]
    return jsonify(data)


def create_bp(app):
    app.register_blueprint(bp)
