import json

from flask import Flask, request, send_file, render_template, redirect

from app_service_server import *
from blueprints.json_api import create_bp
from middleware.io import create_io

app = Flask(__name__)  # nome
io = create_io(app)
create_bp(app)


@app.route('/')
def home():
    home_info = {}
    with open("./home.json", "r", encoding="utf-8") as file:
        home_info = json.loads(file.read())
    return render_template("home.html", home_info=home_info)


@app.route('/folders_view')
def folders_view():
    return render_template("folders_view.html", all_folders=get_all_folders(),
                           all_folders_dumped=json.dumps(get_all_folders()))


@app.route('/reset-simulation-data')
def reset_simulation_data():
    io.emit("reset_simulation")
    return ("", 204)


@app.route('/store/new-simulation', methods=['POST'])
def store_and_init_new_simulation():
    data = request.json
    date = get_date_formatted()
    hour = get_hour_formatted()
    store_firebase_data = data | {"data": date,
                                  "hora": hour, "data_hora": f"{date} {hour}"}

    folder_incompleted = get_folder_uncompleted()
    stored = True
    if len(folder_incompleted) == 0:
        new_folder_name, new_folder = get_new_folder_info_template()
        new_folder[new_folder_name]["Sensores"] = [store_firebase_data]
        print(f"nova pasta a ser registrada: {new_folder}")
        register_new_folder(new_folder)
        data["folder_name"] = new_folder_name
        print(f"criou pasta - Armazenou o data: {store_firebase_data}")
    else:
        stored = False
        folder_name, folder_data = folder_incompleted[0]
        folder_data[folder_name]["Sensores"].append(store_firebase_data)
        print(f"Armazenou o data: {store_firebase_data}")
        register_new_folder(folder_data)
        data["folder_name"] = folder_name

    print(f"data enviado para a VM: {data}")
    io.emit("insert_queue", data)
    io.emit("corrent_data_updater", get_date_and_sensors_values_for_graph(folder_incompleted))
    response_status = {"status": "stored" if stored else "updated", "folder_name": data["folder_name"],
                       "data_stored": store_firebase_data}
    return response_status


@app.route("/simulation/dashboard/<folder>")
def simulation_dashboard(folder):
    folder_completed = get_folder_status_completed(folder)

    if folder_completed is False:
        return redirect(location="/to/uncompleted-simulation/dashboard")

    graph_data_dumped = get_date_and_sensors_values_for_graph_by_folder(folder)
    return render_template("simulation_dashboard.html",
                           data_img=[] if check_images_exist(folder) is False else get_image_data(folder),
                           graph_data=graph_data_dumped, folder_name=folder)


@app.route("/uncompleted-simulation/dashboard/<folder>")
def uncompleted_simulation_dashboard(folder):
    status_folder = get_folder_status_completed(folder)
    if status_folder:
        return redirect(location=f"/simulation/dashboard/{folder}")
    if status_folder is None:
        return "Folder not found", 404
    if check_images_exist(folder):
        return render_template("uncompleted_simulation_dashboard.html", data=get_image_data(folder), folder_name=folder)
    return render_template("uncompleted_simulation_dashboard.html", data=[], folder_name=folder)


@app.route("/to/uncompleted-simulation/dashboard")
def to_uncompleted_simulation_dashboard():
    folder_uncompleted = get_folder_uncompleted()
    if len(folder_uncompleted) == 0:
        return redirect(location="/")
    return redirect(location=f"/uncompleted-simulation/dashboard/{folder_uncompleted[0][0]}")


@app.route('/download/<filename>/<start>/<end>', methods=['GET'])
@app.route('/download/<filename>', methods=['GET'])
@app.route('/download/<filename>/', methods=['GET'])
def download(filename, start=-1, end=-1):
    get_excel_of_folder(filename, int(start), int(end))
    filename = filename + "_Data.xls" if ".xls" not in filename else filename
    return send_file(get_bytes_file(filename), mimetype='application/xls', as_attachment=True,
                     download_name=filename)


@app.route('/download-all/', methods=['GET'])
def download_all_data():
    get_excel_all_folders()
    all_data_file_name = "All_Sensors_Data.xls"
    return send_file(get_bytes_file(all_data_file_name), mimetype='application/xls', as_attachment=True,
                     download_name=all_data_file_name)


@app.route('/delete/<folder>', methods=['POST'])
def delete_folder(folder):
    firebase_delete_folder(folder)
    return "", 204


@app.route('/complete/<folder>', methods=['POST'])
def complete_folder(folder):
    firebase_set_completed_folder(folder)
    return "", 204


if __name__ == "__main__":
    io.run(app, host="0.0.0.0", port=8080, allow_unsafe_werkzeug=True)
