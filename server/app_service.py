#Funções serviços dos aplicativos
import csv
import datetime
import time
import json
import os
import shutil
from datetime import date
from requests import get, post, patch
from log_handler import write_log
from firebase_admin import credentials, initialize_app, storage

link_bd_base = "https://simulacao-femm-default-rtdb.firebaseio.com/"

link_bd = link_bd_base+"/medicoes/{}/.json"
link_bd_folders = link_bd.format("Pastas")
link_bd_todos_sensores = link_bd_base+"/medicoes/.json"
link_bd_image = "simulacao-femm.appspot.com"
link_bd_image_gs = f"gs://{link_bd_image}"

def pegar_data_formatada():
    data_atual = date.today()  # date é a lib
    return "{}/{}/{}".format(data_atual.day, data_atual.month, data_atual.year)  # formatando a data contatenar dados

def pegar_hora_formatada():
    now = datetime.datetime.now()  # agora pegar a hora
    return str(now.hour).zfill(2) + ":" + str(now.minute).zfill(2) + ":" + str(now.second).zfill(2)  # concatenar o foamato da hora

def pegar_nome_pasta():
    data_atual = date.today()
    data_atual = "{}-{}-{}".format(str(data_atual.day).zfill(2), str(data_atual.month).zfill(2), data_atual.year)

    time_now = datetime.datetime.now()  # agora pegar a hora
    milliseconds = str(round(time.time() * 1000, 4))[-4:].replace(".", "")

    time_now = str(time_now.hour).zfill(2) + "-" + str(time_now.minute).zfill(2) + "-" + str(time_now.second).zfill(2) + "-" + str(
        milliseconds)  # concatenar o foamato da hora

    nome_pasta = f'{data_atual}_{time_now}'

    return nome_pasta

def pegar_nova_pasta_formatada():
    nova_pasta_name = pegar_nome_pasta()
    nova_pasta = {
        nova_pasta_name:
            {
                "Sensores":
                {
                    "SensorA": [],
                    "SensorB": [],
                    "SensorC": [],
                    "SensorRPM": [],
                    "SensorTemp": [],
                    "SensorTensao": []
                },
                "completed": False
            }
    }

    return nova_pasta_name, nova_pasta

def register_new_folder(folder_data):
    patch(link_bd_folders, json=folder_data)


def escrever_dados_arquivo_csv(dados): #dados parametros aula lira
    for sensor in dados:
        cols = ['data', 'hora', 'medicao']  # titulo da coluna botando do mesmo jeito do bd
        with open(f"./outputs/{sensor}_output.csv", 'w') as f:  # to abrindo um arquivo csv
            wr = csv.DictWriter(f, fieldnames=cols)  # organizador
            wr.writeheader()  # titulo
            wr.writerows(dados[sensor]) # dados de cada coluna
    shutil.make_archive('output', 'zip', './', 'server/outputs')


def get_folder_incompleted():
    folders = get(link_bd_folders).json()
    folder_incompleted = [(folder, {folder: folders[folder]}) for folder in folders if "completed" in folders[folder] and folders[folder]["completed"] is False]
    return folder_incompleted



def registrar_dado_no_bd(dados, sensor):
    post(link_bd.format(sensor), json=dados)

def pegar_dados_do_sensor(sensor):
    dados_json = json.loads(get(link_bd.format(sensor)).text) #objeto json que pode ser manuseada
    dados_json = [dados_json[x] for x in dados_json] #formatando dados
    return dados_json

def pegar_todos_dados_bd():
    dados_json = json.loads(get(link_bd_todos_sensores).text)  # objeto json que pode ser manuseada
    dados_formatados = {}
    for sensor in dados_json:
        dados_formatados[sensor] = [dados_json[sensor][x] for x in dados_json[sensor]]
    print(dados_formatados)
    return dados_formatados

def pegar_ultimo_dado_do_sensor(sensor):
    dados = pegar_dados_do_sensor(sensor)
    return dados[-1] #estou pegando o ultimo valor enviado

def enviar_pasta_dos_resultados_simulacao(pasta):
    UploadBlob(pasta)

def UploadBlob(folder):

    try:
        cred = credentials.Certificate("./cred.json")
        initialize_app(cred, {'storageBucket': f'{link_bd_image}'})
    except:
        pass

    bucket = storage.bucket(f"{link_bd_image}")

    data_send_socket = []
    for file in os.listdir(folder):
        file_name = f'{folder}/{file}'
        blob = bucket.blob(file_name)
        blob.upload_from_filename(file_name)
        blob.make_public()
        write_log(f"-Upload file: {file_name} | link: {blob.public_url}\n")
        type = "TERMICO" if "TERMICO" in file else "T" if "T" in file else "M"
        data_send_socket.append({"type": type, "name": file, "img": blob.public_url})
    with open("img_send.json", "w") as file:
        file.write(json.dumps(data_send_socket))

def second_to_hour_minute(diferenca):
    if diferenca >= 3600:
        hora = int(diferenca / 60 / 60)
        minutos = int(diferenca / 60) % 60
        segundos = diferenca % 60
        return f"{hora:0>2}h{minutos:0>2}m{segundos:0>2}s"
    if diferenca >= 60:
        minutos = int(diferenca / 60)
        segundos = int(diferenca % 60)
        return f"{int(minutos):0>2}m{segundos:0>2}s"
    return f"{diferenca}s"