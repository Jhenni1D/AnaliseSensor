from flask_socketio import SocketIO
from app_service_server import *


def create_io(app):
    io = SocketIO(app)

    @io.event
    def start_att_img():
        io.emit("send_img_loop")

    @io.event
    def start_simulation_loop():
        io.emit("simulation_loop")

    @io.event
    def request_update_image(data_img):
        print(data_img)
        io.emit("update_image", data_img)

    @io.event
    def progress(prog_value):
        if prog_value == '':
            return
        prog = round(float(prog_value), 2)
        prog = max(0.0, min(prog, 100.0))
        io.emit("progress_value", prog)

    @io.event
    def progress_test():
        # comment return to test
        return
        progress_value = 0
        data = [
            {
                "type": "M",
                "name": "M0",
                "img": "M0"
            },
            {
                "type": "M",
                "name": "M1",
                "img": "M1"
            },
            {
                "type": "M",
                "name": "M2",
                "img": "M2"
            },
            {
                "type": "M",
                "name": "M3",
                "img": "M3"
            },
            {
                "type": "T",
                "name": "T0",
                "img": "T0"
            },
            {
                "type": "T",
                "name": "T1",
                "img": "T1"
            },
            {
                "type": "T",
                "name": "T2",
                "img": "T2"
            },
            {
                "type": "T",
                "name": "T3",
                "img": "T3"
            },
            {
                "type": "TERMICO",
                "name": "TERMICO",
                "img": "TERMICO"
            },
            {
                "type": "TEMPERATURA",
                "name": "TEMPERATURA",
                "img": "TEMPERATURA"
            },
            {
                "type": "TENSAO",
                "name": "TENSAO",
                "img": "TENSAO"
            },
            {
                "type": "VELOCIDADE",
                "name": "VELOCIDADE",
                "img": "VELOCIDADE"
            },
            {
                "type": "EFICIENCIA",
                "name": "EFICIENCIA",
                "img": "EFICIENCIA"
            }
        ]
        for d in range(len(data)):
            while progress_value < 100:
                io.emit("progress_value", round(progress_value, 2))
                progress_value += 1
                time.sleep(0.01)
            progress_value = 0
            io.emit("update_image", data[0:d + 1])
        io.emit("update_image", data)

    @io.event
    def ping():
        io.emit("pong")
        print("send pong")

    @io.event
    def corrent_data_updater(folder):
        io.emit("corrent_data_updater", get_date_and_sensors_values_for_graph_by_folder(folder))
        time.sleep(1)

    @io.event
    def log_simulation(log_text):
        io.emit("log_simulation", log_text)

    return io
