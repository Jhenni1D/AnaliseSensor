from time import sleep

from app_service_server import *
from flask_socketio import SocketIO


def create_io(app):
    io = SocketIO(app)

    @io.event
    def send_img_loop():
        sleep(1)
        io.emit("send_img_loop")

    @io.event
    def simulation_loop():
        sleep(1)
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
                "img": "/static/image_test/M0.png"
            },
            {
                "type": "M",
                "name": "M1",
                "img": "/static/image_test/M1.png"
            },
            {
                "type": "M",
                "name": "M2",
                "img": "/static/image_test/M2.png"
            },
            {
                "type": "M",
                "name": "M3",
                "img": "/static/image_test/M3.png"
            },
            {
                "type": "T",
                "name": "T0",
                "img": "/static/image_test/T0.png"
            },
            {
                "type": "T",
                "name": "T1",
                "img": "/static/image_test/T1.png"
            },
            {
                "type": "T",
                "name": "T2",
                "img": "/static/image_test/T2.png"
            },
            {
                "type": "T",
                "name": "T3",
                "img": "/static/image_test/T3.png"
            }
        ]
        for d in range(len(data)):
            while progress_value < 100:
                io.emit("progress_value", round(progress_value, 2))
                progress_value += 1
                time.sleep(0.05)
            progress_value = 0
            io.emit("update_image", data[0:d + 1])
        io.emit("update_image", data)

    @io.event
    def ping():
        io.emit("pong")
        print("send pong")

    @io.event
    def corrent_data_updater(folder):
        sleep(2)
        io.emit("corrent_data_updater", get_date_and_sensors_values_for_graph_by_folder(folder))

    @io.event
    def log_simulation(log_text):
        io.emit("log_simulation", log_text)

    @io.event
    def reset_simulation_status(status):
        io.emit("reset_simulation_status", status)

    @io.event
    def request_status_vm():
        io.emit("request_status_vm")
        sleep(1)

    @io.event
    def completed_simulation():
        io.emit("completed_simulation")
        sleep(1)

    return io
