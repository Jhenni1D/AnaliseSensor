# Funções serviços dos aplicativos
import datetime
import time
import json
from datetime import date
from requests import get, patch

link_bd_base = "https://simulacao-femm-default-rtdb.firebaseio.com/"

link_bd = link_bd_base + "/medicoes/{}/.json"
link_bd_folders = link_bd.format("Pastas")
link_bd_image = "simulacao-femm.appspot.com"
link_bd_image_gs = f"gs://{link_bd_image}"


def get_date_formatted():
    today = date.today()  # date é a lib
    return "{}/{}/{}".format(str(today.day).zfill(2), str(today.month).zfill(2),
                             str(today.year).zfill(2))  # formatando a data contatenar dados


def get_hour_formatted():
    now = datetime.datetime.now()  # agora pegar a hora
    return str(now.hour).zfill(2) + ":" + str(now.minute).zfill(2) + ":" + str(now.second).zfill(
        2)  # concatenar o foamato da hora


def get_folder_name():
    today = date.today()
    today = "{}-{}-{}".format(str(today.day).zfill(2), str(today.month).zfill(2), today.year)

    time_now = datetime.datetime.now()  # agora pegar a hora
    milliseconds = str(round(time.time() * 1000, 4))[-4:].replace(".", "")

    time_now = str(time_now.hour).zfill(2) + "-" + str(time_now.minute).zfill(2) + "-" + str(time_now.second).zfill(
        2) + "-" + str(
        milliseconds)  # concatenar o foamato da hora

    folder_name = f'{today}_{time_now}'

    return folder_name


def get_new_folder_info_template():
    new_folder_name = get_folder_name()
    new_folder = {
        new_folder_name:
            {
                "Sensores": [],
                "completed": False
            }
    }
    return new_folder_name, new_folder


def register_new_folder(folder_data):
    patch(link_bd_folders, json=folder_data)


def write_csv_data(dados):  # dados parametros aula lira
    # TODO: refazer a criação do CSV
    pass
    # for sensor in dados:
    #     cols = ['data', 'hora', 'medicao']  # titulo da coluna botando do mesmo jeito do bd
    #     with open(f"./outputs/{sensor}_output.csv", 'w') as f:  # to abrindo um arquivo csv
    #         wr = csv.DictWriter(f, fieldnames=cols)  # organizador
    #         wr.writeheader()  # titulo
    #         wr.writerows(dados[sensor])  # dados de cada coluna
    # shutil.make_archive('output', 'zip', './', 'server/outputs')


def get_folder_uncompleted():
    folders = get(link_bd_folders).json()
    folder_uncompleted = [(folder, {folder: folders[folder]}) for folder in folders if
                          "completed" in folders[folder] and folders[folder]["completed"] is False]
    return folder_uncompleted


# TODO: ajustar método
def get_sensor_data(sensor):
    json_data = get(link_bd.format(sensor)).json()  # objeto json que pode ser manuseada
    json_data = [json_data[x] for x in json_data]  # formatando dados
    return json_data


# TODO: ajustar método
def get_all_sensors():
    json_data = get(link_bd_folders).json()  # objeto json que pode ser manuseada
    formatted_data = {}
    for sensor in json_data:
        formatted_data[sensor] = [json_data[sensor][x] for x in json_data[sensor]]
    print(formatted_data)
    return formatted_data


# TODO: ajustar método
def get_last_sensor_data(sensor):
    data = get_sensor_data(sensor)
    return data[-1]  # estou pegando o ultimo valor enviado


def get_date_and_sensors_values_for_graph():
    folders_data = get_folder_uncompleted()
    if len(folders_data) == 0:
        return {}
    folder_name, folder_data = folders_data[0]
    sorted_sensors = sorted(folder_data[folder_name]['Sensores'], key=lambda d: d['data_hora'])
    data_graph = {}
    keys = list(sorted_sensors[0].keys())
    for data in sorted_sensors:
        for key in keys:
            if key not in data_graph:
                data_graph[key] = []
            data_graph[key].append(data[key])
    del data_graph['data']
    del data_graph['hora']
    return data_graph


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
