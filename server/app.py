from flask import Flask, request, send_file, render_template, jsonify
import os
from AnaliseSensor.services.app_service import pegar_data_formatada, \
    pegar_hora_formatada, \
    escrever_dados_arquivo_csv, \
    registrar_dado_no_bd, \
    pegar_todos_dados_bd, \
    pegar_ultimo_dado_do_sensor

from flask_socketio import SocketIO
import json
from requests import get

app = Flask(__name__)  # nome
io = SocketIO(app)


# primeira rota
@app.route('/')
def home():  # def = função
  return "aqui"


@app.route('/nova-simulacao')
def nova_simulacao():  # def = função
  io.emit("reset_simulation")
  return "Arquivos de simulação resetados!"


# segunda rota
# @io.on('receber', namespace='/dados')
@app.route('/dados',
           methods=['POST'])  # dizer o metodo da rota, nesse caso é post
def receber():  # o tipo da função
  dado = request.json  # requisitando um arquivo json
  dado_armazenar = {"medicao": dado["medicao"]}  # dicionario ou objeto
  dado_armazenar["data"] = pegar_data_formatada()
  dado_armazenar["hora"] = pegar_hora_formatada()
  dado["datahora"] = dado_armazenar["data"] + "_" + dado_armazenar["hora"]
  print(f"\nDado armazenado: {dado_armazenar} - Sensor: {dado['sensor']}")
  registrar_dado_no_bd(dado_armazenar, dado["sensor"])
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
  return render_template("pastas.html", pastas=pastas)


@app.route("/visualizar/<pasta>")
def visualizar_pasta(pasta):
  link_folder = f"https://firebasestorage.googleapis.com/v0/b/itutor-32257.appspot.com/o/{pasta}%2FM0.png"

  folder_exist = get(link_folder).status_code.real != 404

  if folder_exist:
    print("PAsta existe")
    link = f"https://firebasestorage.googleapis.com/v0/b/itutor-32257.appspot.com/o/{pasta}%2F{'{}'}.png?alt=media&token=eec1cda6-c13b-43af-a475-84d1b4518c33"
    data = [
      {
        "type": "M",
        "name": "M0",
        "img": link.format("M0")
      },
      {
        "type": "M",
        "name": "M1",
        "img": link.format("M1")
      },
      {
        "type": "M",
        "name": "M2",
        "img": link.format("M2")
      },
      {
        "type": "M",
        "name": "M3",
        "img": link.format("M3")
      },
      {
        "type": "T",
        "name": "T0",
        "img": link.format("T0")
      },
      {
        "type": "T",
        "name": "T1",
        "img": link.format("T1")
      },
      {
        "type": "T",
        "name": "T2",
        "img": link.format("T2")
      },
      {
        "type": "T",
        "name": "T3",
        "img": link.format("T3")
      },
      {
        "type": "TERMICO",
        "name": "TERMICO",
        "img": link.format("TERMICO")
      },
    ]
    return render_template("medicoes.html", data=data)
  return render_template("medicoes.html", data=[])


@io.event
def criar_pasta(pasta):
  pastas = []
  with open("folders.json", "r") as file:
    pastas = json.loads(file.read())
    if pasta not in pastas:
      pastas.append(pasta)
    print("\n\nPASTAS:", pastas)
  with open("folders.json", "w") as file:
    file.write(json.dumps(pastas))
  io.emit("create_folder", pastas)


@io.event
def start_att_img():
  io.emit("send_img_loop")


@io.event
def start_simulation_loop():
  io.emit("simulation_loop")


@io.event
def att_data_image(data_img):
  for data in data_img:
    io.emit("plot_image", data)


@io.event
def progress(prog_value):
  io.emit("progress_value", prog_value)


# cors = CORS(app, resource={r"/*": {"origins": "*"}})


def main():
  io.run(app=app,
         debug=True,
         host="0.0.0.0",
         port=5000,
         allow_unsafe_werkzeug=True)


if __name__ == "__main__":
  main()
