import json
import os
import random
import sys
import time

from AnaliseSensor.VM.FEMM_Simulation import FEMMSimulationController
from app_service import pegar_ultimo_dado_do_sensor, enviar_pasta_dos_resultados_simulacao, pegar_data_formatada, \
    pegar_hora_formatada, second_to_hour_minute
from AnaliseSensor.VM.log_handler import write_log


class SimulationController:
    def __init__(self):
        self.simulations = {
            "0": {"done": False, "range": 2, "in_queue": False},
            "1": {"done": False, "range": 3.2, "in_queue": False},
            "2": {"done": False, "range": 3.9, "in_queue": False},
            "3": {"done": False, "range": 4, "in_queue": False},
            "4": {"done": False, "range": 4.3, "in_queue": False},
            "actual_simulation": 0,
            "index_queue": 0,
            "folder_name": ""
        }
        self.LIMIT_RANGE = 5
        self.femm = FEMMSimulationController()

    def reset(self):
        self.simulations = {
            "0": {"done": False, "range": 2, "in_queue": False},
            "1": {"done": False, "range": 3.2, "in_queue": False},
            "2": {"done": False, "range": 3.9, "in_queue": False},
            "3": {"done": False, "range": 4, "in_queue": False},
            "4": {"done": False, "range": 4.3, "in_queue": False},
            "actual_simulation": 0,
            "index_queue": 0,
            "folder_name": ""
        }
        self.femm.reset()
        if os.path.exists("femm_generate_files") is False:
            os.mkdir("femm_generate_files")
        for file in os.listdir("femm_generate_files"):
            os.remove(f"./femm_generate_files/{file}")
        for file in os.listdir("../"):
            if "simulation" in file and ".json" in file:
                os.remove(f"./{file}")
        with open("simulation.json", "w") as file:
            file.write(json.dumps(self.simulations, indent=1))

    def load_simulation(self):
        with open("simulation.json") as file:
            self.simulations = json.loads(file.read())

    def is_can_start_simulation(self, range):  # quando as condições forem satisfestas
        actual_simulation = self.simulations["actual_simulation"]

        is_simulation_done = self.simulations[str(actual_simulation)]["done"]
        is_simulation_in_range = range >= self.simulations[str(actual_simulation)]["range"]
        is_range_in_limit = range < self.LIMIT_RANGE
        return is_range_in_limit and is_simulation_done is False and is_simulation_in_range

    def is_can_enqueue(self, range):
        self.load_simulation()
        index = str(self.simulations["index_queue"])
        if index not in self.simulations:
            return False
        return self.simulations[index]["in_queue"] is False and float(range) >= self.simulations[index]["range"]

    def hash_generate(self):
        letras = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "m", "n", "o", "p", "q", "z", "A", "B"
                  "C", "D", "E", "F", "G", "H", "I", "J", "M"]
        return "".join(random.choices(letras, k=10))

    def reset_config_if_index_out_of_range(self):
        if str(self.simulations["actual_simulation"]) not in self.simulations:
            write_log(f"# RESET AUTOMATICO\n-Index {self.simulations['actual_simulation']} ultrapassa limite. Resetando dados e iniciando "
                      f"nova simulação do 0.\n\n")
            self.reset()
            with open("simulation.json", "w") as file:
                file.write(json.dumps(self.simulations, indent=1))

    def update_queue(self):
        self.simulations[str(self.simulations["index_queue"])]["in_queue"] = True
        self.simulations["index_queue"] += 1
        with open("simulation.json", "w") as file:
            file.write(json.dumps(self.simulations, indent=1))

    def start_simulation(self, range, sensor):
        start = time.time()
        try:
            self.load_simulation()
            self.reset_config_if_index_out_of_range()
        except Exception as e:
            print("Exception in load_simulation or reset_config: ", e.args)


        if (self.is_can_start_simulation(range) is False and sensor != "SensorA"):  # sai da simulaçao e define sensor
            return

        try:
            if self.simulations["actual_simulation"] == 0:
                new_folder = self.hash_generate()
                os.mkdir(new_folder)
                self.simulations["folder_name"] = new_folder
                write_log(f"-Criou pasta com o nome: {self.simulations['folder_name']}\n", folder=self.simulations["folder_name"], create=True)

                with open("folder_name.txt", "w") as file:
                    file.write(new_folder)
        except Exception as e:
            msg = f"Exception in create folder: {e.args}"
            print(msg)
            write_log(f"\n{msg}")

        try:
            write_log(f"# INICIO DA SIMULAÇÃO {self.simulations['actual_simulation']}: {pegar_data_formatada()}_{pegar_hora_formatada()}\n", folder=self.simulations["folder_name"])
            sensorB = float(pegar_ultimo_dado_do_sensor("SensorB")["medicao"])
            sensorC = float(pegar_ultimo_dado_do_sensor("SensorC")["medicao"])
            write_log(
                f"# MEDICAO_A: {range} | B: {sensorB} | C: {sensorC}")
            self.femm.set_femm_atributes(ca=range, cb=sensorB, cc=sensorC,
                                         index=self.simulations["actual_simulation"],
                                         first=self.simulations["actual_simulation"] == 0,
                                         folder_name=self.simulations["folder_name"])
        except Exception as e:
            msg = f"Exception in get SensorB/C and set femm attributes: {e.args}"
            print(msg)
            write_log(f"\n# MEDICAO_A: {range} | B: {sensorB} | C: {sensorC}\n{msg}")


        try:
            self.femm.iniciar_femm()
        except Exception as e:
            msg = f"Exception when try init femm: {e.args}"
            print(msg)
            write_log(f"\n{msg}")

        try:
            write_log(f"-Finalizou simulação\n")
            self.simulations[str(self.simulations["actual_simulation"])]["done"] = True
            self.simulations["actual_simulation"] += 1
            enviar_pasta_dos_resultados_simulacao(self.simulations["folder_name"])
            write_log(f"-Finalizou de enviar imagens para o Firebase\n")
            print("Finalizou:", self.simulations["folder_name"])
            with open("simulation.json", "w") as file:
                file.write(json.dumps(self.simulations, indent=1))
            write_log(f"-Atualizou o arquivo simulation.json\n")
            write_log(f"-arquivo simulation.json: {json.dumps(self.simulations)}\n")
            finish = time.time()
            write_log(f"# FIM DA SIMULACAO: {pegar_data_formatada()}_{pegar_hora_formatada()} - TEMPO DE EXECUÇÃO: {second_to_hour_minute(finish - start)}\n")
        except Exception as e:
            msg = f"Exception in finalize: {e.args}"
            print(msg)
            write_log(f"\n{msg}")


def main(args):
    s = SimulationController()
    try:
        data = json.loads(args[1])
        rangeA, sensor = float(data[0]), data[1]
    except Exception as e:
        print("Excpetion in main:", e.args)
    s.start_simulation(rangeA, sensor)


if __name__ == "__main__":
    teste = [2121, json.dumps(['2.5', '2.5', '2.5', 'SensorA'])]
    main(sys.argv)#sys.argv | teste = json.dumps(['4.65', 'SensorA'])
