import json
import os
import subprocess
import sys
import time
import queue
import socketio

import simulation


class LoopState:

    def __init__(self):
        self.simulation_running = False
        self.files_running = False

sio = socketio.Client()
fila = queue.Queue()
file_simulation = os.path.abspath("simulation.py").replace("\\", "/")
simulation_controller = simulation.SimulationController()
simulation_state = LoopState()

@sio.event
def connect():
    sio.emit("start_att_img")
    sio.emit("start_simulation_loop")
    print('connection established')


@sio.event
def insert_queue(data):
    simulation_controller.load_simulation()
    if simulation_controller.is_can_enqueue(data["medicao"]):
        fila.put(data)
        simulation_controller.update_queue()
        print("Inseriu elemento na fila, elementos na fila:", fila.qsize(), " | dados:", data)



@sio.event
def simulation_loop():
    if simulation_state.simulation_running:
        print("Loop simulação já está rodando!")
        return
    while True:
        simulation_state.simulation_running = True
        while not fila.empty():
            data = fila.get()
            print('Irá iniciar simulação com os dados:', data)
            p = subprocess.run([sys.executable, file_simulation, json.dumps([data["medicao"], data["sensor"]])],
                               capture_output=True, text=True)
            print("LOG EXECUCAO SUBPROCESS:", p.stdout)
    simulation_state.simulation_running = False

@sio.event
def send_img_loop():
    if simulation_state.files_running:
        print("Loop dos arquivos já está rodando!")
        return
    print("Iniciou o loop dos arquivos")
    img_file_name = "img_send.json"
    folder_file_name = "folder_name.txt"
    progress_file_name = "progress_simulation.txt"
    while True:
        simulation_state.files_running = True
        time.sleep(3)
        dir_list = os.listdir("../")
        if img_file_name in dir_list:
            try:
                with open(img_file_name) as file:
                    sio.emit('att_data_image', json.loads(file.read()))
                os.remove(img_file_name)
            except:
                print("Quebrou ao tentar abrir arquivo das imagens")

        if folder_file_name in dir_list:
            try:
                with open(folder_file_name) as file:
                    sio.emit('criar_pasta', file.read())
                os.remove(folder_file_name)
            except:
                print("Quebrou ao tentar abrir arquivo de pasta")

        if progress_file_name in dir_list:
            try:
                with open(progress_file_name) as file:
                    sio.emit('progress', file.read())
            except:
                print("Quebrou ao tentar abrir arquivo progress")
    print("Finalizou Loop")
    simulation_state.files_running = False


@sio.event
def reset_simulation():
    simu = simulation.SimulationController()
    simu.reset()
    print('Arquivos de simulação Resetados!')

@sio.event
def disconnect():
    print('disconnected from server')


sio.connect('https://JhenniSensor.eliko.repl.co')
sio.wait()

#codigo do femm