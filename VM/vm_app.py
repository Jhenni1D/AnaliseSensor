import json
import os
import queue
import subprocess
import time

import socketio

import simulation_controller_executor


class LoopState:

    def __init__(self):
        self.simulation_running = False
        self.files_running = False


sio = socketio.Client()
queue = queue.Queue()
simulation_controller = simulation_controller_executor.SimulationController()
simulation_state = LoopState()

try:
    @sio.event
    def connect():
        sio.emit("ping")
        print("send ping")

        sio.emit("send_img_loop")
        sio.emit("simulation_loop")
        print('Loops starteds')

        sio.emit("request_status_vm")
        print('status vM started')

    @sio.event
    def pong():
        print("receive pong")


    @sio.event
    def insert_queue(data):
        simulation_controller.load_simulation()
        is_can_enqueue = simulation_controller.is_can_enqueue(data["SensorA"])
        if is_can_enqueue:
            queue.put(data)
            print("Inseriu elemento na fila, elementos na fila:", queue.qsize(), " | dados:", data)
            simulation_controller.update_queue(data["folder_name"])



    @sio.event
    def simulation_loop():

        if simulation_state.simulation_running:
            return

        time.sleep(2)

        while not queue.empty():
            simulation_state.simulation_running = True
            data = queue.get()
            print('Irá iniciar simulação com os dados:', data)
            args = f"./simulation_controller_executor.exe \"{json.dumps(data).replace('"', "'")}\""
            # args_test = f"./.vm-venv/Scripts/python ./simulation_controller_executor.py \"{json.dumps(data).replace('"', "'")}\""
            # args = args_test
            with subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE) as proc:
                try:
                    stdout_simulation = proc.stdout.read().decode()
                except Exception as e:
                    print("Exception in stout of simulation.exe")
                    stdout_simulation = proc.stdout.read().decode("latin-1")
                print(f"LOG DO PROCESSo: \n---\n{stdout_simulation}\n---\n")
        simulation_state.simulation_running = False
        try:
            sio.emit("simulation_loop")
        except:
            pass


    @sio.event
    def send_img_loop():
        time.sleep(3)
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


    @sio.event
    def reset_simulation():
        simu = simulation_controller_executor.SimulationController()
        simu.reset()
        sio.emit("reset_simulation_status", True)
        print('Arquivos de simulação Resetados!')


    @sio.event
    def request_status_vm():
        time.sleep(2)
        try:
            sio.emit("request_status_vm")
        except:
            pass


    @sio.event
    def disconnect():
        print('disconnected from server')


    sio.connect("https://server-sensor.fly.dev/")  # https://server-sensor.fly.dev/ | http://localhost:8080/
    sio.wait()
except Exception as e:
    print(e)
    input()