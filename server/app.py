import random

from flask import Flask, request, send_file, render_template, jsonify, redirect, url_for
import os
from app_service import *

from flask_socketio import SocketIO
import json
from requests import get
import time

app = Flask(__name__)  # nome
io = SocketIO(app)

sensor_names = {
    "SensorC1": "SensorA",
    "SensorC2": "SensorB",
    "SensorC3": "SensorC"
}

# primeira rota
@app.route('/')
def home():  # def = função
    return render_template("home.html")


@app.route('/nova-simulacao')
def nova_simulacao():  # def = função
    io.emit("reset_simulation")
    return "Arquivos de simulação resetados!"


@app.route('/dados',
           methods=['POST'])  # dizer o metodo da rota, nesse caso é post
def receber():  # o tipo da função
    dado = request.json  # requisitando um arquivo json

    if dado["sensor"] in ["SensorC1", "SensorC2", "SensorC3"]:
        actual_name = dado["sensor"]
        dado["sensor"] = sensor_names[actual_name]

    dado_armazenar = {"medicao": dado["medicao"], "data": pegar_data_formatada(),
                      "hora": pegar_hora_formatada()}  # dicionario ou objeto

    dado["datahora"] = dado_armazenar["data"] + "_" + dado_armazenar["hora"]

    folder_incompleted = get_folder_incompleted()
    if len(folder_incompleted) == 0:
        new_folder_name, new_folder = pegar_nova_pasta_formatada()
        new_folder[new_folder_name]["Sensores"][dado['sensor']].append(dado_armazenar)
        print(f"nova pasta a ser registrada: {new_folder}")
        register_new_folder(new_folder)
        dado["folder_name"] = new_folder_name
        print(f"criou pasta - Armazenou o dado: {dado_armazenar}")
    else:
        folder_name, folder_data = folder_incompleted[0]

        if dado['sensor'] not in folder_data[folder_name]["Sensores"]:
            folder_data[folder_name]["Sensores"][dado['sensor']] = []

        folder_data[folder_name]["Sensores"][dado['sensor']].append(dado_armazenar)
        print(f"Armazenou o dado: {dado_armazenar}")
        register_new_folder(folder_data)
        dado["folder_name"] = folder_name


    if "sensora" == dado["sensor"].lower():
        print(f"dado enviado para a VM: {dado}")
        io.emit("insert_queue", dado)
    return "deu tudo certo"


# terceira rota de baixar os dados em formato de excel
@app.route("/baixar_dado")
def baixar_dado():
    escrever_dados_arquivo_csv(pegar_todos_dados_bd())
    path = os.getcwd() + "/output.zip"  # caminho do codigo atual
    return send_file(
        path, as_attachment=True
    )  # send_file do flask pegue o arquivo do direotiro pra poder baixar


@app.route("/visualizar_dado")
def visualizar_dado():
    return jsonify(pegar_todos_dados_bd())


@app.route("/ultimo-dado-sensor/<sensor>")
def ultimo_dado_sensor(sensor):
    return jsonify(pegar_ultimo_dado_do_sensor(sensor))


@app.route("/pastas")
def visualizar_pastas():
    pastas = []
    with open("folders.json", "r") as file:
        pastas = json.loads(file.read())
    return jsonify(pastas)

def check_and_get_img(link, folder_img, all_folders):
    img_link = link if folder_img in all_folders else "https://cdn.dribbble.com/users/386433/screenshots/1689880/placehold.gif"
    return img_link


def get_image_data(pasta):
    link_all_folders_imgs = "https://firebasestorage.googleapis.com/v0/b/simulacao-femm.appspot.com/o/"
    all_folders = get(link_all_folders_imgs).json()['items']
    all_folders = [data_img['name'] for data_img in all_folders]
    link = f"https://firebasestorage.googleapis.com/v0/b/simulacao-femm.appspot.com/o/{pasta}%2F{'{}'}.png?alt=media"
    data = [
        {
            "type": "M",
            "name": "M0",
            "img": ""
        },
        {
            "type": "M",
            "name": "M1",
            "img": ""
        },
        {
            "type": "M",
            "name": "M2",
            "img": ""
        },
        {
            "type": "M",
            "name": "M3",
            "img": ""
        },
        {
            "type": "T",
            "name": "T0",
            "img": ""
        },
        {
            "type": "T",
            "name": "T1",
            "img": ""
        },
        {
            "type": "T",
            "name": "T2",
            "img": ""
        },
        {
            "type": "T",
            "name": "T3",
            "img": ""
        },
        {
            "type": "TERMICO",
            "name": "TERMICO",
            "img": ""
        }
    ]
    for d in data:
        d["img"] = check_and_get_img(link.format(d["name"]), f'{pasta}/{d["name"]}.png', all_folders)
    return data


@app.route("/visualizar/<pasta>")
def visualizar_pasta(pasta):
    link_folder = f"https://firebasestorage.googleapis.com/v0/b/simulacao-femm.appspot.com/o/{pasta}%2FM0.png"
    folder_exist = get(link_folder).status_code.real != 404

    if folder_exist:
        return render_template("medicoes3.html", data=get_image_data(pasta))
    return render_template("medicoes3.html", data=[])


@app.route("/ultima-pasta")
def ultima_pasta():
    data = {"pasta": None}
    folder_incompleted = get_folder_incompleted()
    if len(folder_incompleted) != 0:
        data["pasta"] = folder_incompleted[0][0]
    return jsonify(data)


@app.route("/dashboard/ultima-pasta")
def dashboard_ultima_pasta():
    folder_incompleted = get_folder_incompleted()
    if len(folder_incompleted) == 0:
        return redirect(url_for("/"))
    print(folder_incompleted[0][0])
    return redirect(location=f"/visualizar/{folder_incompleted[0][0]}")

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


if __name__ == "__main__":
    io.run(app, host="0.0.0.0", port=8080, allow_unsafe_werkzeug=True)
