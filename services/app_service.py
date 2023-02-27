#Funções serviços dos aplicativos
import csv
import datetime
import json
import os
import shutil
from datetime import date
from requests import get, post
from AnaliseSensor.VM.log_handler import write_log
from firebase_admin import credentials, initialize_app, storage
link_bd = "https://itutor-32257-default-rtdb.firebaseio.com/medicoes/{}/.json"
link_bd_todos_sensores = "https://itutor-32257-default-rtdb.firebaseio.com/medicoes/.json"
link_bd_image = "gs://itutor-32257.appspot.com/"

def pegar_data_formatada():
    data_atual = date.today()  # date é a lib
    return "{}/{}/{}".format(data_atual.day, data_atual.month,data_atual.year)  # formatando a data contatenar dados

def pegar_hora_formatada():
    now = datetime.datetime.now()  # agora pegar a hora
    return str(now.hour) + ":" + str(now.minute) + ":" + str(now.second)  # concatenar o foamato da hora

def escrever_dados_arquivo_csv(dados): #dados parametros aula lira
    for sensor in dados:
        cols = ['data', 'hora', 'medicao']  # titulo da coluna botando do mesmo jeito do bd
        with open(f"server/outputs/{sensor}_output.csv", 'w') as f:  # to abrindo um arquivo csv
            wr = csv.DictWriter(f, fieldnames=cols)  # organizador
            wr.writeheader()  # titulo
            wr.writerows(dados[sensor]) # dados de cada coluna
    shutil.make_archive('output', 'zip', './', 'server/outputs')

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
        cred = credentials.Certificate("C:/Users/elielson/PycharmProjects/SMAM/cred.json")
        initialize_app(cred, {'storageBucket': 'itutor-32257.appspot.com/'})
    except:
        pass

    bucket = storage.bucket("itutor-32257.appspot.com")

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
