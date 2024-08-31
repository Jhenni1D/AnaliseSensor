# Funções serviços dos aplicativos
import datetime
import io
import os
import time
from datetime import date

from requests import get, patch, delete
from xlwt import Workbook

link_bd_base = "https://simulacao-femm-2-default-rtdb.firebaseio.com/"

link_bd = link_bd_base + "/medicoes/Pastas/{}.json"
link_bd_folders = link_bd.format("")
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


def get_folder_filter(filter_folder):
    folders = get(link_bd_folders).json()
    if folders is None:
        return []
    folder_filtred = [[folder, {folder: folders[folder]}] for folder in folders if
                      filter_folder(folder, folders[folder])]
    return folder_filtred


def get_all_folders():
    all_folders = get_folder_filter(lambda fn, fd: True)
    return all_folders


def get_folder_uncompleted():
    def filter_folder(folder_name, folder_data):
        return "completed" in folder_data and folder_data["completed"] is False

    folder_uncompleted = get_folder_filter(filter_folder)
    return folder_uncompleted


def get_folder_status_completed(folder):
    folder_info = get_folder_filter(lambda folder_name, folder_d: folder_name == folder)
    status = folder_info[0][1][folder_info[0][0]]["completed"]
    return status


def get_formatted_sensors_data(folders_data):
    folder_name, folder_data = folders_data
    sorted_sensors = sorted(folder_data[folder_name]['Sensores'], key=lambda d: d['data_hora'])
    data_graph = {}
    keys = list(sorted_sensors[0].keys())
    for data in sorted_sensors:
        for key in keys:
            if key not in data_graph:
                data_graph[key] = []
            if key in data:
                data_graph[key].append(data[key])
    del data_graph['data']
    del data_graph['hora']
    return data_graph


def get_date_and_sensors_values_for_graph_uncompleted():
    folders_data = get_folder_uncompleted()
    if len(folders_data) == 0:
        return {}
    return get_formatted_sensors_data(folders_data[0])


def get_date_and_sensors_values_for_graph_by_folder(folder):
    folder_data = get_folder_filter(lambda fn, fd: fn == folder)
    if len(folder_data) == 0:
        return {}
    return get_formatted_sensors_data(folder_data[0])


def get_excel_all_folders(start_limit=0, end_limit=0):
    all_folders_data = get_all_folders()
    all_folders_formatted = []
    all_folders_data_info = {}
    for folders_data in all_folders_data:
        all_folders_formatted.append(get_formatted_sensors_data(folders_data))
    for data in all_folders_formatted:
        for key in data:
            if key not in all_folders_data_info:
                all_folders_data_info[key] = []
            all_folders_data_info[key] += data[key]
    get_excel_of_data("All_Sensors", all_folders_data_info)


def get_excel_of_folder(folder, start_limit=-1, end_limit=-1):
    folder_data = get_folder_filter(lambda folder_name, folder_d: folder_name == folder)
    if len(folder_data) == 0:
        return

    folder_data = get_formatted_sensors_data(folder_data[0])
    if start_limit < end_limit and start_limit > -1:
        for key in folder_data:
            folder_data[key] = folder_data[key][start_limit:end_limit+1]
    print(folder_data)
    get_excel_of_data(folder, folder_data)


def get_excel_of_data(file_name, data):
    wb = Workbook()
    sheet1 = wb.add_sheet(f'Sensor Data', cell_overwrite_ok=True)
    # sheet1.write(coluna, linha, 'Value')
    sheet1.write(0, 0, "Data")
    datetime_sensor = data['data_hora']
    del data['data_hora']
    for i in range(1, len(datetime_sensor) + 1):
        sheet1.write(i, 0, datetime_sensor[i - 1])
        for sensor in data:
            if i == 1:
                sheet1.write(0, list(data.keys()).index(sensor) + 1, sensor)
            sheet1.write(i, list(data.keys()).index(sensor) + 1, data[sensor][i - 1])
    wb.save(f'{file_name}_Data.xls')


def check_and_get_img(link, folder_img, all_folders):
    img_link = link if folder_img in all_folders else "https://cdn.dribbble.com/users/386433/screenshots/1689880/placehold.gif"
    return img_link


def get_bytes_file(filename):
    file_path = f"./{filename}"
    return_data = io.BytesIO()
    with open(file_path, 'rb') as fo:
        return_data.write(fo.read())
    return_data.seek(0)
    os.remove(file_path)
    return return_data


def firebase_delete_folder(folder):
    delete(link_bd.format(folder))

def firebase_set_completed_folder(folder):
    folder_info = get_folder_filter(lambda folder_name, folder_d: folder_name == folder)
    folder_info[0][1][folder_info[0][0]]["completed"] = True
    patch(link_bd.format(folder), json=folder_info[0][1][folder])

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
