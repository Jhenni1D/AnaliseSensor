#Funções serviços dos aplicativos
import csv
import datetime
import json
import shutil
from datetime import date
from requests import get,post

link_bd = "https://itutor-32257-default-rtdb.firebaseio.com/medicoes/{}/.json"
link_bd_todos_sensores = "https://itutor-32257-default-rtdb.firebaseio.com/medicoes/.json"

def pegar_data_formatada():
    data_atual = date.today()  # date é a lib
    return "{}/{}/{}".format(data_atual.day, data_atual.month,data_atual.year)  # formatando a data contatenar dados

def pegar_hora_formatada():
    now = datetime.datetime.now()  # agora pegar a hora
    return str(now.hour) + ":" + str(now.minute) + ":" + str(now.second)  # concatenar o foamato da hora

def escrever_dados_arquivo_csv(dados): #dados parametros aula lira
    for sensor in dados:
        cols = ['data', 'hora', 'medicao']  # titulo da coluna botando do mesmo jeito do bd
        with open(f"outputs/{sensor}_output.csv", 'w') as f:  # to abrindo um arquivo csv
            wr = csv.DictWriter(f, fieldnames=cols)  # organizador
            wr.writeheader()  # titulo
            wr.writerows(dados[sensor]) # dados de cada coluna
    shutil.make_archive('output', 'zip', './', 'outputs')

def registrar_dado_no_bd(dados, sensor):
    post(link_bd.format(sensor), json=dados)

def pegar_dados_do_sensor(sensor):
    dados_json = json.loads(get(link_bd.format(sensor)).text) #objeto json que pode ser manuseada
    dados_json = [dados_json[x] for x in dados_json] #formatando dados
    print(dados_json)
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

