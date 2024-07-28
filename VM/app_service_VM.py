# Funções serviços dos aplicativos
from firebase_admin import credentials, initialize_app, storage
from log_handler import write_log
from requests import get, patch
from datetime import date
import datetime
import json
import os

link_bd = "https://simulacao-femm-2-default-rtdb.firebaseio.com/medicoes/{}/.json"
link_bd_folders = link_bd.format("Pastas")
link_bd_image = "simulacao-femm.appspot.com"
link_bd_image_gs = f"gs://{link_bd_image}"


def get_formatted_date():
    toay = date.today()  # date é a lib
    return "{}/{}/{}".format(str(toay.day).zfill(2), str(toay.month).zfill(2), toay.year)  # formatando a data contatenar dados


def get_formatted_hour():
    now = datetime.datetime.now()  # agora pegar a hora
    return str(now.hour).zfill(2) + ":" + str(now.minute).zfill(2) + ":" + str(now.second).zfill(2)  # concatenar o foamato da hora


def set_completed_simulation():
    folders = get(link_bd_folders).json()
    folder_pending = [(folder, {folder: folders[folder]}) for folder in folders if
                      folders[folder]["completed"] is False]
    if len(folder_pending) == 0:
        print("definir_simulacao_completed - Folder peding not exist")
        return
    folder_name, folder_pending = folder_pending[0]
    folder_pending[folder_name]["completed"] = True
    patch(link_bd_folders, json=folder_pending)


def send_simulation_images_to_firebase(folder):
    upload_blob(folder)


def upload_blob(folder):
    try:
        cred = credentials.Certificate("./cred_firebase_server.json")
        initialize_app(cred, {'storageBucket': f'{link_bd_image}/'})
    except:
        print("ERRO AO INICIALIZAR APP FIREBASE")
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
        data_send_socket.append({"type": type, "name": file.split(".")[0], "img": blob.public_url})
    with open("img_send.json", "w") as file:
        file.write(json.dumps(data_send_socket))


def second_to_hour_minute(second):
    if second >= 3600:
        hour = int(second / 60 / 60)
        minute = int(second / 60) % 60
        new_second = second % 60
        return f"{hour:0>2}h{minute:0>2}m{new_second:0>2}s"
    if second >= 60:
        minute = int(second / 60)
        new_second = int(second % 60)
        return f"{int(minute):0>2}m{new_second:0>2}s"
    return f"{second}s"
