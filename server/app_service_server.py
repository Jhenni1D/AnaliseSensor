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


def get_folder_incompleted():
    folders = get(link_bd_folders).json()
    folder_incompleted = [(folder, {folder: folders[folder]}) for folder in folders if
                          "completed" in folders[folder] and folders[folder]["completed"] is False]
    return folder_incompleted


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
    folders_data = get_folder_incompleted()
    if len(folders_data) == 0:
        return {}
    folder_name, folder_data = folders_data[0]
    sensors_names = [fn for fn in folder_data[folder_name]["Sensores"] if fn in ['SensorA', 'SensorB', 'SensorC']]
    list_unpacked_unique_values = lambda list_filter: list(
        {a for b in [{y for y in x} for x in list_filter] for a in b})
    list_unpacked = lambda list_filter: [a for b in [[y for y in x] for x in list_filter] for a in b]
    list_unpacked_hashed = lambda list_filter: {list(x.keys())[0]: x[list(x.keys())[0]] for x in list_filter}

    sensors = folder_data[folder_name]['Sensores']

    def del_sensor_not_need(sensor_name):
        if sensor_name in sensors:
            del sensors[sensor_name]

    del_sensor_not_need("SensorRPM")
    del_sensor_not_need("SensorTemp")
    del_sensor_not_need("SensorTensao")
    all_values = [
        [{f"{sensor_info['data']} {sensor_info['hora']}": {"sensor": sensor, "value": sensor_info['medicao']}} for
         sensor_info in sensors[sensor]] for sensor in sensors]
    all_values = list_unpacked(all_values)
    all_values_hashed = list_unpacked_hashed(all_values)
    all_dates = [[f"{sensor_info['data']} {sensor_info['hora']}" for sensor_info in sensors[sensor]] for sensor in
                 sensors]
    all_dates = list_unpacked_unique_values(all_dates)
    all_dates.sort()

    sensor_data = lambda sensor_name: [all_values_hashed[d]['value'] for d in all_dates if
                                       sensor_name in all_values_hashed[d]['sensor']]

    graph_data = {sensor_name: sensor_data(sensor_name) for sensor_name in sensors_names}
    graph_data["dates"] = all_dates
    return graph_data