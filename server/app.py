from flask import Flask, request, send_file, render_template, redirect, url_for
from blueprints.json_api import create_bp
from middleware.io import create_io
from app_service_server import *
from requests import get
import os

app = Flask(__name__)  # nome
io = create_io(app)
create_bp(app)


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


@app.route("/uncompleted-simulation/dashboard/<folder>")
def uncompleted_simulation_dashboard(folder):
    link_folder = f"https://firebasestorage.googleapis.com/v0/b/simulacao-femm.appspot.com/o/{folder}%2FM0.png"
    folder_exist = get(link_folder).status_code.real != 404

    if folder_exist:
        return render_template("medicoes3.html", data=get_image_data(folder), folder_name=folder)
    return render_template("medicoes3.html", data=[], folder_name=folder)


@app.route("/to/uncompleted-simulation/dashboard")
def to_uncompleted_simulation_dashboard():
    folder_uncompleted = get_folder_uncompleted()
    if len(folder_uncompleted) == 0:
        return redirect(url_for("/"))
    print(folder_uncompleted[0][0])
    return redirect(location=f"/uncompleted-simulation/dashboard/{folder_uncompleted[0][0]}")


if __name__ == "__main__":
    io.run(app, host="0.0.0.0", port=8080, allow_unsafe_werkzeug=True)
