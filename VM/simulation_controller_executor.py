import random
import sys
import time

from FEMM_Simulation import FEMMSimulationController
from app_service_VM import *
from log_handler import write_log


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
        self.LIMIT_RANGE = 15
        self.femm = FEMMSimulationController()

    def reset(self):
        self.load_simulation()
        self.simulations = {
            "0": {"done": False, "range": 2, "in_queue": False},
            "1": {"done": False, "range": 3.2, "in_queue": False},
            "2": {"done": False, "range": 3.9, "in_queue": False},
            "3": {"done": False, "range": 4, "in_queue": False},
            "4": {"done": False, "range": 4.3, "in_queue": False},
            "actual_simulation": 0,
            "index_queue": 0,
            "folder_name": self.simulations["folder_name"]
        }
        self.femm.reset()
        if os.path.exists("./femm_generate_files") is False:
            os.mkdir("./femm_generate_files")
        for file in os.listdir("./femm_generate_files"):
            os.remove(f"./femm_generate_files/{file}")
        for file in os.listdir("./"):
            if "simulation" in file and ".json" in file:
                os.remove(f"./{file}")
            if f"log-simulacao_" in file:
                with open(f"./{file}", "w") as f:
                    f.write("")
            if "progress_simulation" in file:
                with open(f"./{file}", "w") as f:
                    f.write("0")


        with open("./simulation.json", "w") as file:
            file.write(json.dumps(self.simulations, indent=1))

    def load_simulation(self):
        with open("./simulation.json") as file:
            self.simulations = json.loads(file.read())

    def is_can_start_simulation(self, range):  # quando as condições forem satisfestas
        self.load_simulation()
        actual_simulation = self.simulations["actual_simulation"]

        is_simulation_done = self.simulations[str(actual_simulation)]["done"]
        is_simulation_in_range = range >= self.simulations[str(actual_simulation)]["range"]
        is_range_in_limit = range < self.LIMIT_RANGE
        msg = ""
        
        if is_simulation_done:
            msg = f"Error: The simulation {actual_simulation} is DONE"
        if is_simulation_in_range is False:
            msg = f"Error: The range {range} is over what actual range {self.simulations[str(actual_simulation)]["range"]}"
        if is_range_in_limit is False:
            msg = f"Error: range {range} is over the simulation limit: {self.LIMIT_RANGE}"
        
        if msg != "":
            print(msg)
            folder_name = self.simulations["folder_name"]
            write_log(msg, folder=folder_name)
        return is_range_in_limit and is_simulation_done is False and is_simulation_in_range

    def is_can_enqueue(self, range):
        self.load_simulation()
        index = str(self.simulations["index_queue"])
        if index not in self.simulations:
            return False
        return self.simulations[index]["in_queue"] is False and float(range) >= self.simulations[index]["range"]

    def hash_generate(self):
        letras = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "m", "n", "o", "p", "q", "z", "A", "B"
                                                                                                       "C", "D", "E",
                  "F", "G", "H", "I", "J", "M"]
        return "".join(random.choices(letras, k=10))

    def update_queue(self, folder_name):
        self.simulations["folder_name"] = folder_name
        self.simulations[str(self.simulations["index_queue"])]["in_queue"] = True
        self.simulations["index_queue"] += 1
        with open("./simulation.json", "w") as file:
            file.write(json.dumps(self.simulations, indent=1))

    def invalid_queue_reset(self):
        print(
            f"will reset: index queue: {self.simulations["index_queue"]} | in queue: {self.simulations[str(self.simulations["index_queue"])]["in_queue"]}")
        if 0 > (self.simulations["index_queue"] - 1) > 4:
            print(f"invalid index_queue: {(self.simulations["index_queue"] - 1)}")
            return
        self.simulations["index_queue"] -= 1
        self.simulations[str(self.simulations["index_queue"])]["in_queue"] = False
        with open("./simulation.json", "w") as file:
            file.write(json.dumps(self.simulations, indent=1))

    def is_folder_exist(self):
        return self.simulations["folder_name"] in os.listdir("./")

    def start_simulation(self, range_sensorA, range_sensorB, range_sensorC, temp):
        start = time.time()
        try:
            self.load_simulation()
        except Exception as e:
            print("Exception in load_simulation or reset_config: ", e.args)

        if self.is_can_start_simulation(range_sensorA) is False:
            # Isso aqui serve pra ele iniciar a simulação apenas com o sensorA.
            # Devido a isso, todos os outros dados devem ser setados anteriormente.
            # SensorA deve ser enviado por último.
            return

        try:
            if self.simulations["actual_simulation"] == 0 and self.is_folder_exist() is False:
                os.mkdir(self.simulations["folder_name"])
                write_log(f"-Criou pasta com o nome: {self.simulations['folder_name']}\n",
                          folder=self.simulations["folder_name"], create=True)

                with open("./folder_name.txt", "w") as file:
                    file.write(self.simulations["folder_name"])
        except Exception as e:
            msg = f"Exception in create folder: {e.args}"
            print(msg)
            write_log(f"\n{msg}")

        sensorB = -1
        sensorC = -1
        try:
            write_log(
                f"# INICIO DA SIMULAÇÃO {self.simulations['actual_simulation']}: {get_formatted_date()}_{get_formatted_hour()}\n",
                folder=self.simulations["folder_name"])
            write_log(
                f"# MEDICAO_A: {range_sensorA} | B: {sensorB} | C: {sensorC}")
            self.femm.set_femm_atributes(ca=range_sensorA, cb=range_sensorB, cc=range_sensorC, temperatura=temp,
                                         index=self.simulations["actual_simulation"],
                                         first=self.simulations["actual_simulation"] == 0,
                                         folder_name=self.simulations["folder_name"])
        except Exception as e:
            msg = f"Exception in get SensorB/C and set femm attributes: {e.args}"
            print(msg)
            write_log(f"\n# MEDICAO_A: {range_sensorA} | B: {sensorB} | C: {sensorC}\n{msg}")
        finished_simulation_correctaly = False
        try:
            self.femm.iniciar_femm()
            finished_simulation_correctaly = True
        except Exception as e:
            msg = f"Exception when try init femm: {e.args}"
            print(msg)
            write_log(f"\n{msg}")

        try:
            if finished_simulation_correctaly:
                write_log(f"-Finalizou simulação\n")
                self.load_simulation()
                self.simulations[str(self.simulations["actual_simulation"])]["done"] = True
                self.simulations["actual_simulation"] += 1
                send_simulation_images_to_firebase(self.simulations["folder_name"])
                write_log(f"-Finalizou de enviar imagens para o Firebase\n")
                print("Finalizou:", self.simulations["folder_name"])
                with open("./simulation.json", "w") as file:
                    file.write(json.dumps(self.simulations, indent=1))
                write_log(f"-Atualizou o arquivo simulation.json\n")
                write_log(f"arquivo simulation.json: {json.dumps(self.simulations)}\n")
                finish = time.time()
                write_log(
                    f"# FIM DA SIMULACAO: {get_formatted_date()}_{get_formatted_hour()} - TEMPO DE EXECUÇÃO: {second_to_hour_minute(finish - start)}\n")
                print("simulation finished")
                if self.simulations["actual_simulation"] == 5:
                    set_completed_simulation()
                    self.reset()
                    write_log(f"\n# FINALIZOU AS SIMULAÇÕES PARA A PASTA: {self.simulations['folder_name']}")
            else:
                print("FEMM simulation not completed!")
                self.load_simulation()
                self.invalid_queue_reset()

        except Exception as e:
            msg = f"Exception in finalize: {e.args}"
            print(msg)
            write_log(f"\n{msg}")


def main(args):
    s = SimulationController()
    try:
        data = json.loads(args[1].replace("\'", '\"'))
        print(f"Irá iniciar a simulação com os dados: {data}")
        s.start_simulation(data["SensorA"], data["SensorB"], data["SensorC"], data["SensorTemp"])
    except Exception as e:
        print("Excpetion in main:", e.args, "\n\n", args)


if __name__ == "__main__":
    main(sys.argv)
