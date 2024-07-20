from flask import Flask, request, send_file, render_template, jsonify, redirect, url_for
import os
from app_service_server import *
from flask_socketio import SocketIO
from requests import get
import time

app = Flask(__name__)  # nome
io = SocketIO(app)


# primeira rota
@app.route('/')
def home():  # def = função
    return render_template("home.html")


@app.route('/reset-simulation-data')
def nova_simulacao():  # def = função
    io.emit("reset_simulation")
    return "Simulation data deleteds!"


@app.route('/store/new-simulation', methods=['POST'])
def store_and_init_new_simulation():
    data = request.json
    date = get_date_formatted()
    hour = get_hour_formatted()
    store_firebase_data = data | {"data": date,
                             "hora": hour, "data_hora": f"{date} {hour}"}

    folder_incompleted = get_folder_uncompleted()
    if len(folder_incompleted) == 0:
        new_folder_name, new_folder = get_new_folder_info_template()
        new_folder[new_folder_name]["Sensores"] = [store_firebase_data]
        print(f"nova pasta a ser registrada: {new_folder}")
        register_new_folder(new_folder)
        data["folder_name"] = new_folder_name
        print(f"criou pasta - Armazenou o data: {store_firebase_data}")
    else:
        folder_name, folder_data = folder_incompleted[0]
        folder_data[folder_name]["Sensores"].append(store_firebase_data)
        print(f"Armazenou o data: {store_firebase_data}")
        register_new_folder(folder_data)
        data["folder_name"] = folder_name

    print(f"data enviado para a VM: {data}")
    io.emit("insert_queue", data)
    return "deu tudo certo"


# terceira rota de baixar os dados em formato de excel
@app.route("/download-simulation-data")
def download_simulation_data():
    write_csv_data(get_all_sensors())
    path = os.getcwd() + "/output.zip"  # caminho do codigo atual
    return send_file(
        path, as_attachment=True
    )  # send_file do flask pegue o arquivo do direotiro pra poder baixar


@app.route("/show-data/.json")
def show_data():
    return jsonify(get_all_sensors())

#TODO: ajustar rota e seu método
@app.route("/last-sensor-data/<sensor>/.json")
def last_sensor_data(sensor):
    return jsonify(get_last_sensor_data(sensor))


@app.route("/uncompleted-simulation/dashboard/<folder>")
def uncompleted_simulation_dashboard(folder):
    link_folder = f"https://firebasestorage.googleapis.com/v0/b/simulacao-femm.appspot.com/o/{folder}%2FM0.png"
    folder_exist = get(link_folder).status_code.real != 404

    if folder_exist:
        return render_template("medicoes3.html", data=get_image_data(folder), folder_name=folder)
    return render_template("medicoes3.html", data=[], folder_name=folder)


@app.route("/uncompleted-simulation/.json")
def uncompleted_simulation():
    data = {"folder": None}
    folder_uncompleted = get_folder_uncompleted()
    if len(folder_uncompleted) != 0:
        data["folder"] = folder_uncompleted[0][0]
    return jsonify(data)


@app.route("/to/uncompleted-simulation/dashboard")
def uncompleted_simulation_dashboard():
    folder_uncompleted = get_folder_uncompleted()
    if len(folder_uncompleted) == 0:
        return redirect(url_for("/"))
    print(folder_uncompleted[0][0])
    return redirect(location=f"/visualizar/{folder_uncompleted[0][0]}")


@io.event
def start_att_img():
    io.emit("send_img_loop")


@io.event
def start_simulation_loop():
    io.emit("simulation_loop")


@io.event
def request_update_image(data_img):
    print(data_img)
    io.emit("update_image", data_img)


@io.event
def progress(prog_value):
    if prog_value == '':
        return
    prog = round(float(prog_value), 2)
    prog = max(0.0, min(prog, 100.0))
    io.emit("progress_value", prog)


@io.event
def progress_test():
    # comment return to test
    return
    progress_value = 0
    data = [
        {
            "type": "M",
            "name": "M0",
            "img": "M0"
        },
        {
            "type": "M",
            "name": "M1",
            "img": "M1"
        },
        {
            "type": "M",
            "name": "M2",
            "img": "M2"
        },
        {
            "type": "M",
            "name": "M3",
            "img": "M3"
        },
        {
            "type": "T",
            "name": "T0",
            "img": "T0"
        },
        {
            "type": "T",
            "name": "T1",
            "img": "T1"
        },
        {
            "type": "T",
            "name": "T2",
            "img": "T2"
        },
        {
            "type": "T",
            "name": "T3",
            "img": "T3"
        },
        {
            "type": "TERMICO",
            "name": "TERMICO",
            "img": "TERMICO"
        },
        {
            "type": "TEMPERATURA",
            "name": "TEMPERATURA",
            "img": "TEMPERATURA"
        },
        {
            "type": "TENSAO",
            "name": "TENSAO",
            "img": "TENSAO"
        },
        {
            "type": "VELOCIDADE",
            "name": "VELOCIDADE",
            "img": "VELOCIDADE"
        },
        {
            "type": "EFICIENCIA",
            "name": "EFICIENCIA",
            "img": "EFICIENCIA"
        }
    ]
    for d in range(len(data)):
        while progress_value < 100:
            io.emit("progress_value", round(progress_value, 2))
            progress_value += 1
            time.sleep(0.01)
        progress_value = 0
        io.emit("update_image", data[0:d + 1])
    io.emit("update_image", data)


@io.event
def ping():
    io.emit("pong")
    print("send pong")


@io.event
def corrent_data_updater():
    while True:
        io.emit("corrent_data_updater", get_date_and_sensors_values_for_graph())
        time.sleep(1)


if __name__ == "__main__":
    io.run(app, host="0.0.0.0", port=8080, allow_unsafe_werkzeug=True)
