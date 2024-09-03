import json
import os
import queue
import subprocess
import time

import socketio

import simulation_controller_executor
from log_handler import write_log, set_folder_log


class LoopState:
    MAX_RETRY_SIMULATION = 6
    def __init__(self):
        self.simulation_running = False
        self.files_running = False
        self.current_retry_simulation = 0
        self.simulation_process: subprocess.Popen[bytes] = None
        self.cancel_simulation = False

    def is_max_retry(self) -> bool:
        is_max_retry = self.current_retry_simulation <= LoopState.MAX_RETRY_SIMULATION
        self.current_retry_simulation += 1
        return is_max_retry


sio = socketio.Client()
data_queue = queue.Queue()
simulation_controller = simulation_controller_executor.SimulationController()
simulation_state = LoopState()
link_server = "https://server-sensor.fly.dev/"  # https://server-sensor.fly.dev/ | http://localhost:8080/

@sio.event
def connect():
    sio.emit("ping")
    print("send ping")
    sio.emit("simulation_loop")


@sio.event
def pong():
    print("receive pong")


@sio.event
def insert_queue(data):
    simulation_controller.load_simulation()
    is_can_enqueue = simulation_controller.is_can_enqueue(data["SensorA"])
    if is_can_enqueue:
        data["link"] = link_server
        data_queue.put(data)
        print("Inseriu elemento na fila, elementos na fila:", data_queue.qsize(), " | dados:", data)
        simulation_controller.update_queue(data["folder_name"])


@sio.event
def reset_simulation():
    simu = simulation_controller_executor.SimulationController()
    simu.reset()
    sio.emit("reset_simulation_status", True)
    print('Arquivos de simulação Resetados!')


@sio.event
def disconnect():
    print('disconnected from server')


@sio.event
def cancel():
    simulation_state.cancel_simulation = True
    sio.emit("cancel_confirmation")
    global data_queue
    data_queue = queue.Queue()
    reset_simulation()


@sio.event
def simulation_loop():
    time.sleep(1)
    while not data_queue.empty():
        simulation_state.simulation_running = True
        data = data_queue.get()
        simulation_completed = False
        current_simulation_index = simulation_controller.get_current_simulation_index()
        set_folder_log(data["folder_name"])
        msg = f'Irá iniciar simulação com os dados: {data}'
        print(msg)
        write_log(msg)
        retry_count = 1
        while simulation_completed is False and simulation_state.cancel_simulation is False:
            msg = f"Tentativa: {retry_count}"
            print(msg)
            write_log(msg)

            if retry_count > 0 and retry_count % LoopState.MAX_RETRY_SIMULATION == 0:
                write_log(
                    f"\n# Tentativas ultrapassou o limite de {LoopState.MAX_RETRY_SIMULATION}, permitindo cancelamento!\n")
                sio.emit("enable_cancel")

            args = f"./simulation_controller_executor.exe \"{json.dumps(data).replace('"', "'")}\""
            # args_test = f"./.vm-venv/Scripts/python ./simulation_controller_executor.py \"{json.dumps(data).replace('"', "'")}\""
            # args = args_test
            with subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True) as proc:
                try:
                    simulation_state.simulation_process = proc
                    stdout_simulation = proc.stdout.read()
                except Exception as e:
                    print("Exception in stout of simulation.exe")
                    stdout_simulation = proc.stdout.read()
                print(f"LOG DO PROCESSo: \n---\n{stdout_simulation}\n---\n")
            simulation_completed = simulation_controller.is_simulation_completed(current_simulation_index)
            retry_count += 1

    if simulation_controller.is_completed_last_simulation():
        sio.emit("completed_simulation")

    simulation_state.cancel_simulation = False
    simulation_state.simulation_running = False
    try:
        sio.emit("simulation_loop")
    except:
        pass


def send_img_loop():
    time.sleep(1)
    img_file_name = "img_send.json"
    progress_file_name = "progress_simulation.txt"
    simulation_controller.load_simulation()

    dir_list = os.listdir("./")
    if img_file_name in dir_list:
        try:
            with open(img_file_name) as file:
                sio.emit('request_update_image', json.loads(file.read()))
            os.remove(img_file_name)
        except Exception as ex:
            simulation_state.files_running = False
            print(f"Quebrou ao tentar abrir arquivo das imagens:\n{ex}")

    if progress_file_name in dir_list:
        try:
            with open(progress_file_name) as file:
                sio.emit('progress', file.read())
        except Exception as ex:
            simulation_state.files_running = False
            print(f"Quebrou ao tentar abrir arquivo progress:\n{ex}")

    log_file = f"log-simulacao_{simulation_controller.simulations["folder_name"]}.txt"
    if log_file in dir_list:
        try:
            with open(f"./{log_file}", encoding="utf-8") as file:
                sio.emit('log_simulation', file.read())
        except Exception as ex:
            simulation_state.files_running = False
            print(f"Quebrou ao tentar abrir o arquivo de log:\n {ex}")

    try:
        sio.emit("send_img_loop")
    except:
        pass


def request_status_vm():
    time.sleep(2)
    emitted = False
    while emitted is False:
        try:
            sio.emit("request_status_vm")
            emitted = True
        except:
            pass


sio.connect(link_server)

while True:
    send_img_loop()
    request_status_vm()
