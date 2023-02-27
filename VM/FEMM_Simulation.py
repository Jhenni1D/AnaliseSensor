import os
import time

import femm, math, cmath
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import json
from log_handler import write_log


class FEMMSimulationController():

    def __init__(self):
        self.femm_files = "femm_files"
        self.femm_generate_files = "femm_generate_files"
        self.correnteA = 0
        self.correnteB = 0
        self.correnteC = 0
        self.index_simulacao = 0
        self.primeira_simulacao = False
        self.p_estator = []
        self.degrau = math.pi / 180.0
        self.media_enr_estator = []
        self.media_enr_rotor = []

        self.p_rotor = []
        self.pestator = []
        self.protor = []
        self.t_estator = []

        self.cond_est = []
        self.cond_rotor = []

        self.temperatura_enr_estator = []
        self.cond_enr_estator = []
        self.t_rotor = []
        self.temperatura_enr_rotor = []
        self.cond_enr_rotor = []
        self.theta1 = 0
        self.theta2 = 0
        self.theta3 = 0
        self.folder_name = ""

    def load_data(self):
        file_name = f"simulation_{self.folder_name}.json"
        if file_name in os.listdir("../"):
            with open(file_name, "r") as file:
                data = json.loads(file.read())
                data["index_simulacao"] = self.index_simulacao
                data["correnteA"] = self.correnteA
                data["correnteB"] = self.correnteB
                data["correnteC"] = self.correnteC
                data["primeira_simulacao"] = self.primeira_simulacao
                self.__dict__ = data
            write_log("-Arquivo com dados de simulação anterior carregado.\n")

    def save_data(self):
        with open(f"simulation_{self.folder_name}.json", "w") as file:
            file.write(json.dumps(self.__dict__))
        write_log(f"-Salvou dados da simulação {self.index_simulacao}\n")

    def set_femm_atributes(self, ca, cb, cc, index, first, folder_name):
        self.correnteA = ca
        self.correnteB = -cb
        self.correnteC = -cc
        self.index_simulacao = index
        self.primeira_simulacao = first
        self.folder_name = folder_name


    def reset(self):
        self.femm_files = "femm_files"
        self.correnteA = 0
        self.correnteB = 0
        self.correnteC = 0
        self.index_simulacao = 0
        self.primeira_simulacao = False
        self.p_estator = []
        self.degrau = math.pi / 180.0
        self.media_enr_estator = []
        self.media_enr_rotor = []

        self.p_rotor = []
        self.pestator = []
        self.protor = []
        self.t_estator = []

        self.cond_est = []
        self.cond_rotor = []

        self.temperatura_enr_estator = []
        self.cond_enr_estator = []
        self.t_rotor = []
        self.temperatura_enr_rotor = []
        self.cond_enr_rotor = []
        self.theta1 = 0
        self.theta2 = 0
        self.theta3 = 0
        self.folder_name = ""

    def save_progress_simulation(self, value, first=False):
        try:
            with open("progress_simulation.txt", "w") as file:
                file.write(str(value))
        except Exception as e:
            print(e)

    def criando_materiais(self):
        # Cobre para o estator
        for j in range(36):  # faz isso pras 36 ranhuras do motor
            # nome do material, Permeabilidade relativa em x e y,0,0, condutividade eletrica,0,0,volume do ferro,
            # fio magnético,Número de fios na construção do fio, Diâmetro de cada fio constituinte do fio em milímetros.
            femm.mi_addmaterial('Copper_' + str(j) + '_estator', 1, 1, 0, 0, 58, 0, 0, 1, 3, 0, 0, 1, 0.45466985972222)
            # Alumínio para o rotor
        femm.mi_addmaterial('Aluminio_rotor', 1, 1, 0, 0, 34.45, 0, 0, 1, 3, 0, 0, 1, 1)

    def iniciar_femm(self):
        progresso = 4.54
        self.save_progress_simulation(progresso)

        self.load_data()

        femm.openfemm()
        #print("Iniciou FEMM")
        if self.primeira_simulacao:
            femm.opendocument(f'./{self.femm_files}/MOTOR.fem')
            femm.mi_saveas(f'./{self.femm_files}/temp.fem')
            self.criando_materiais()
        else:
            #femm.opendocument(f'./{self.femm_files}/MOTOR.fem')
            femm.opendocument(f'./{self.femm_files}/temp.fem')
            for j in range(36):
                femm.mi_modifymaterial('Copper_' + str(j) + '_estator', 5, self.cond_est[j])

            femm.mi_modifymaterial('Aluminio_rotor', 5, self.cond_enr_rotor[self.index_simulacao - 2])

        self.cond_est.clear()  # zera a self.cond_est

        # Atualização dos materiais dos enrolamentos de cobre
        write_log("-Atualização dos materiais dos enrolamentos de cobre")
        t1 = 5
        for j in range(1, 37):
            k = j - 1
            m = k * 10
            self.theta1 = t1 + m
            #x1 = 48 * math.cos(self.theta1 * self.degrau)
            #y1 = 48 * math.sin(self.theta1 * self.degrau)
            x1 = 5.3278 * math.cos(self.theta1 * self.degrau)
            y1 = 5.3278 * math.sin(self.theta1 * self.degrau)
            #print(x1)
            #print(y1)
            femm.mi_selectlabel(x1, y1)
            # diz qual o sentido do enrolamento
            # o que é ess 44
            # A member of group number group, The number of turns associated with this label is denoted by turns.
            if (k >= 0 and k <= 2) or (k >= 18 and k <= 20):
                femm.mi_setblockprop('Copper_' + str(k) + '_estator', 1, 0, 'C', 0, 1, 44)
                femm.mi_clearselected()
            elif (k >= 3 and k <= 5) or (k >= 21 and k <= 23):
                femm.mi_setblockprop('Copper_' + str(k) + '_estator', 1, 0, 'A', 0, 1, -44)
                femm.mi_clearselected()
            elif (k >= 6 and k <= 8) or (k >= 24 and k <= 26):
                femm.mi_setblockprop('Copper_' + str(k) + '_estator', 1, 0, 'B', 0, 1, 44)
                femm.mi_clearselected()
            elif (k >= 9 and k <= 11) or (k >= 27 and k <= 29):
                femm.mi_setblockprop('Copper_' + str(k) + '_estator', 1, 0, 'C', 0, 1, -44)
                femm.mi_clearselected()
            elif (k >= 12 and k <= 14) or (k >= 30 and k <= 32):
                femm.mi_setblockprop('Copper_' + str(k) + '_estator', 1, 0, 'A', 0, 1, 44)
                femm.mi_clearselected()
            elif (k >= 15 and k <= 17) or (k >= 33 and k <= 35):
                femm.mi_setblockprop('Copper_' + str(k) + '_estator', 1, 0, 'B', 0, 1, -44)
                femm.mi_clearselected()
            femm.mi_clearselected()
            progresso += 0.12 #tava dentro do for
        self.save_progress_simulation(progresso)

        progresso += 4.54
        self.save_progress_simulation(progresso)

        # Atualização dos materiais dos enrolamentos do motor
        write_log("-Atualização dos materiais dos enrolamentos do motor")
        self.theta2 = 0
        for k in range(28):
            self.theta2 = 12.86 * k
            x3 = 3.6923 * math.cos(self.theta2 * self.degrau)
            y3 = 3.6923 * math.sin(self.theta2 * self.degrau)
            #x3 = 33 * math.cos(self.theta2 * self.degrau)
            #y3 = 33 * math.sin(self.theta2 * self.degrau)
            #print(x3)
            #print(y3)
            femm.mi_selectlabel(x3, y3)
            femm.mi_setblockprop('Aluminio_rotor', 1, 0, '<None>', 0, 1, 1)
            femm.mi_clearselected()
            progresso += 0.16
            self.save_progress_simulation(progresso)

        progresso += 4.54
        self.save_progress_simulation(progresso)

        # Modificando o parâmetro ho_blockintegralde corrente do circuito
        write_log("-Modificando o parâmetro ho_blockintegralde corrente do circuito")
        femm.mi_modifycircprop('A', 1, self.correnteA)
        femm.mi_modifycircprop('B', 1, self.correnteB)
        femm.mi_modifycircprop('C', 1, self.correnteC)
        #print(self.correnteA)
        #print(self.correnteB)
        #print(self.correnteC)
        # Solucionando o problema
        progresso += 4.54
        self.save_progress_simulation(progresso)

        write_log("-Criando arquivo temporário M")
        femm.mi_zoomnatural()
        femm.mi_saveas(f'./{self.femm_files}/temp.fem')
        femm.mi_saveas(f'./{self.femm_generate_files}/MAG' + str(60) + str(self.index_simulacao) + '.fem')
        femm.smartmesh(1)  # malha pronta
        femm.mi_analyze(1)
        progresso += 4.54
        self.save_progress_simulation(progresso)

        write_log("-Criando Imagem do resultado colorido")
        femm.mi_loadsolution()  # carrega e exibe a solução correspondente à geometria atual
        femm.mo_showdensityplot(1, 0, 0, 2.774, 'mag')  # Verificar como fica a distribuição de campo
        femm.mo_savebitmap(f'./{self.folder_name}/M{self.index_simulacao}.png')  # salva o resultado em imagem
        femm.mo_hidedensityplot()
        progresso += 4.54
        self.save_progress_simulation(progresso)

        # Perdas resistivas no enrolamento do estator
        m_estator = 0  # t1 = ângulo inicial do estator
        # Lendo perdas no estator
        write_log("-Lendo perdas no estator")
        for j in range(1, 37):
            m = (j - 1) * 10
            self.theta1 = t1 + m
            #x1 = 48 * math.cos(self.theta1 * self.degrau)
            #y1 = 48 * math.sin(self.theta1 * self.degrau)
            x1 = 5.3278 * math.cos(self.theta1 * self.degrau)
            y1 = 5.3278 * math.sin(self.theta1 * self.degrau)
            #print(x1)
            #print(y1)
            femm.mo_seteditmode('area')  #
            femm.mo_selectblock(x1, y1)
            aux = femm.mo_blockintegral(4)
            #print(aux)
            femm.mo_clearblock()
            self.p_estator.append(aux)
            m_estator = m_estator + aux
            progresso += 0.12
            self.save_progress_simulation(progresso)

        progresso += 4.54
        self.save_progress_simulation(progresso)

        m_estator = m_estator / 36
        #print(m_estator)
        self.media_enr_estator.append(m_estator)

        # Perdas nos enrolamentos do rotor
        m_rotor = 0
        # Lendo as perdas no rotor
        write_log("-Lendo perdas no rotor")
        for j in range(0, 28):
            self.theta2 = 12.86 * j
            #x3 = 33 * math.cos(self.theta2 * self.degrau)
            #y3 = 33 * math.sin(self.theta2 * self.degrau)
            x3 = 3.6923 * math.cos(self.theta2 * self.degrau)
            y3 = 3.6923 * math.sin(self.theta2 * self.degrau)
            femm.mo_seteditmode('area')
            femm.mo_selectblock(x3, y3)
            aux = femm.mo_blockintegral(6)
            femm.mo_clearblock()
            self.p_rotor.append(aux)
            m_rotor = m_rotor + aux
            progresso += 0.16
            self.save_progress_simulation(progresso)

        progresso += 4.54
        self.save_progress_simulation(progresso)

        m_rotor = m_rotor / 28  # Valores das barras da gaiola do rotor
        #print(m_rotor)
        self.media_enr_rotor.append(m_rotor)

        # Perdas no estator
        write_log("-Perdas no estator")
        femm.mo_seteditmode('area')
        femm.mo_selectblock(6.6923, 0)
        self.pestator.append(femm.mo_blockintegral(6))
        femm.mo_clearblock()
        progresso += 4.54
        self.save_progress_simulation(progresso)

        # Perdas no rotor
        write_log("-Perdas no rotor")
        femm.mo_seteditmode('area')
        femm.mo_selectblock(2.0769, 0)
        self.protor.append(femm.mo_blockintegral(6))
        femm.mo_clearblock()
        progresso += 4.54
        self.save_progress_simulation(progresso)

        femm.mo_close()
        femm.mi_close()

        ################################################
        # Simulação Térmica
        ################################################
        write_log("-Iniciou simulação térmica")
        femm.opendocument(f'./{self.femm_files}/TERMICO.feh')
        femm.hi_saveas(f'./{self.femm_generate_files}/term_atual.feh')

        femm.hi_probdef('centimeters', 'planar', 1E-8, 30, 30)
        femm.hi_addboundprop("Heat flux", 1, 0, 278000, 0, 0, 0)
        femm.hi_addboundprop("Heat flux1", 1, 0, 0, 0, 0, 0)
        femm.hi_addboundprop("Convection", 2, 0, 0, 300, 30, 0)

        progresso += 4.54
        self.save_progress_simulation(progresso)

        # INSERINDO CONDIÇÃO DE CONTORNO REFERENTE ÀS PERDAS NOS ENROLAMENTOS DO ESTATOR

        #print(self.p_estator)
        # na proxima colocar um comparador da temp interna
        write_log("-Inserindo condição de contorno referente às perdas nos enrolamentos do estator")
        try:
            t1 = 5
            for j in range(36):
                m = j * 10
                self.theta1 = t1 + m

                femm.hi_addconductorprop("Enr_" + str(j) + "_Estator", 0, self.p_estator[j], 0)

                femm.hi_selectarcsegment(5.7692 * math.cos((self.theta1 + 2) * self.degrau),
                                         5.7692 * math.sin((self.theta1 + 2) * self.degrau))  # Superior 1
                femm.hi_setarcsegmentprop(1, "Heat flux", 0, 4, "Enr_" + str(j) + "_Estator")  # pq é 4?
                femm.hi_clearselected()

                femm.hi_selectarcsegment(5.8846 * math.cos((self.theta1 + 0.4) * self.degrau),
                                         5.8846 * math.sin((self.theta1 + 0.4) * self.degrau))  # Superior 2
                femm.hi_setarcsegmentprop(1, "Heat flux", 0, 4, "Enr_" + str(j) + "_Estator")
                femm.hi_clearselected()

                femm.hi_selectarcsegment(5.8846 * math.cos((self.theta1 - 0.4) * self.degrau),
                                         5.8846 * math.sin((self.theta1 - 0.4) * self.degrau))  # Superior 3
                femm.hi_setarcsegmentprop(1, "Heat flux", 0, 4, "Enr_" + str(j) + "_Estator")
                femm.hi_clearselected()

                femm.hi_selectarcsegment(5.7692 * math.cos((self.theta1 - 2) * self.degrau),
                                         5.7692 * math.sin((self.theta1 - 2) * self.degrau))  # Superior 4
                femm.hi_setarcsegmentprop(1, "Heat flux", 0, 4, "Enr_" + str(j) + "_Estator")
                femm.hi_clearselected()

                femm.hi_selectarcsegment(5 * math.cos((self.theta1 + 0.5) * self.degrau),
                                         5 * math.sin((self.theta1 + 0.5) * self.degrau))  # Inferior 1
                femm.hi_setarcsegmentprop(1, "Heat flux", 0, 4, "Enr_" + str(j) + "_Estator")
                femm.hi_clearselected()

                femm.hi_selectarcsegment(5 * math.cos((self.theta1 - 0.5) * self.degrau),
                                         5 * math.sin((self.theta1 - 0.5) * self.degrau))  # Inferior 2
                femm.hi_setarcsegmentprop(1, "Heat flux", 0, 4, "Enr_" + str(j) + "_Estator")
                femm.hi_clearselected()

                femm.hi_selectsegment(4.8 * math.cos((self.theta1 + 0.3) * self.degrau),
                                      4.8 * math.sin((self.theta1 + 0.3) * self.degrau))  # Inferior 3
                femm.hi_setarcsegmentprop(1, "Heat flux", 0, 4, "Enr_" + str(j) + "_Estator")
                femm.hi_clearselected()

                femm.hi_selectsegment(5.3278 * math.cos((self.theta1 + 0.3) * self.degrau),
                                      5.3278 * math.sin((self.theta1 + 0.3) * self.degrau))  # Lado 1
                femm.hi_setarcsegmentprop(1, "Heat flux", 0, 4, "Enr_" + str(j) + "_Estator")
                femm.hi_clearselected()

                femm.hi_selectsegment(5.3278 * math.cos((self.theta1 - 0.3) * self.degrau),
                                      5.3278 * math.sin((self.theta1 - 0.3) * self.degrau))  # Lado 2
                femm.hi_setarcsegmentprop(1, "Heat flux", 0, 4, "Enr_" + str(j) + "_Estator")
                femm.hi_clearselected()
                progresso += 0.12
                self.save_progress_simulation(progresso)
        except Exception as e:
            print("Deu erro no FOR mesmo")
            print(e)

        self.p_estator.clear()
        self.theta3 = 0
        progresso += 4.54
        self.save_progress_simulation(progresso)

        write_log("-Calculo temperatura geral")
        for j in range(28):
            self.theta3 = 12.86 * j
            x3 = 3.6923 * math.cos(self.theta3 * self.degrau)
            y3 = 3.6923 * math.sin(self.theta3 * self.degrau)

            femm.hi_addconductorprop("Enr_" + str(j) + "_Rotor", 0, self.p_rotor[j], 0)

            femm.hi_selectarcsegment(3.6923 * math.cos((self.theta3 + 2) * self.degrau),
                                     3.6923 * math.sin((self.theta3 + 2) * self.degrau))

            # arco superior 1
            femm.hi_setarcsegmentprop(1, "Heat flux1 ", 0, 4, "Enr_" + str(j) + "_Rotor")
            femm.hi_clearselected()

            femm.hi_selectarcsegment(3.6923 * math.cos((self.theta3 - 2) * self.degrau),
                                     3.6923 * math.sin((self.theta3 - 2) * self.degrau))  # arco superior 2
            femm.hi_setarcsegmentprop(1, "Heat flux1 ", 0, 4, "Enr_" + str(j) + "_Rotor")
            femm.hi_clearselected()

            femm.hi_selectsegment(4.5 * math.cos((self.theta3 + 0.2) * self.degrau),
                                  4.5 * math.sin((self.theta3 + 0.2) * self.degrau))  # segmento superior 1
            femm.hi_setarcsegmentprop(1, "Heat flux1 ", 0, 4, "Enr_" + str(j) + "_Rotor")
            femm.hi_clearselected()

            femm.hi_selectsegment(4.5 * math.cos((self.theta3 - 0.2) * self.degrau),
                                  4.5 * math.sin((self.theta3 - 0.2) * self.degrau))  # segmento superior 2
            femm.hi_setarcsegmentprop(1, "Heat flux1 ", 0, 4, "Enr_" + str(j) + "_Rotor")
            femm.hi_clearselected()

            femm.hi_selectsegment(3.6923 * math.cos((self.theta3 - 1) * self.degrau),
                                  3.6923 * math.sin((self.theta3 - 1) * self.degrau))  # segmento lado 1
            femm.hi_setarcsegmentprop(1, "Heat flux1 ", 0, 4, "Enr_" + str(j) + "_Rotor")
            femm.hi_clearselected()

            femm.hi_selectsegment(3.6923 * math.cos((self.theta3 + 1) * self.degrau),
                                  3.6923 * math.sin((self.theta3 + 1) * self.degrau))  # segmento lado 2
            femm.hi_setarcsegmentprop(1, "Heat flux1 ", 0, 4, "Enr_" + str(j) + "_Rotor")
            femm.hi_clearselected()

            femm.hi_selectarcsegment(2.93 * math.cos((self.theta3 + 0.2) * self.degrau),
                                     2.93 * math.sin((self.theta3 + 0.2) * self.degrau))  # arco inferior 1
            femm.hi_setarcsegmentprop(1, "Heat flux1 ", 0, 4, "Enr_" + str(j) + "_Rotor")
            femm.hi_clearselected()

            femm.hi_selectarcsegment(2.93 * math.cos((self.theta3 - 0.2) * self.degrau),
                                     2.93 * math.sin((self.theta3 - 0.2) * self.degrau))  # arco inferior 2
            femm.hi_setarcsegmentprop(1, "Heat flux1 ", 0, 4, "Enr_" + str(j) + "_Rotor")
            femm.hi_clearselected()
            progresso += 0.16
            self.save_progress_simulation(progresso)

        self.p_rotor.clear()

        progresso += 4.54
        self.save_progress_simulation(progresso)

        femm.hi_addconductorprop("Perdas_" + str(self.index_simulacao - 1) + "_Estator", 0,
                                 self.pestator[self.index_simulacao - 1], 0)
        femm.hi_addboundprop("Ambiente", 2, 0, 0, 300, 52, 0)
        # adicionar a temperatura ambiente
        # Perdas no ferro do estator
        write_log("-Setando condições de contorno")
        # Perdas no ferro do estator
        femm.hi_selectarcsegment(5, 5.3)
        femm.hi_setarcsegmentprop(1, "<None>", 0, 4, "Perdas_" + str(self.index_simulacao - 1) + "_Estator")
        femm.hi_clearselected()

        femm.hi_selectarcsegment(5, -5.3)
        femm.hi_setarcsegmentprop(1, "<None>", 0, 4, "Perdas_" + str(self.index_simulacao - 1) + "_Estator")
        femm.hi_clearselected()

        femm.hi_selectarcsegment(-5, -5.3)
        femm.hi_setarcsegmentprop(1, "<None>", 0, 4, "Perdas_" + str(self.index_simulacao - 1) + "_Estator")
        femm.hi_clearselected()

        femm.hi_selectarcsegment(-5, 5.3)
        femm.hi_setarcsegmentprop(1, "<None>", 0, 4, "Perdas_" + str(self.index_simulacao - 1) + "_Estator")
        femm.hi_clearselected()

        # Condição de contorno do ambiente
        femm.hi_selectarcsegment(0, 7.6)
        femm.hi_setarcsegmentprop(1, "Ambiente", 0, 4, "<None>")
        femm.hi_clearselected()

        femm.hi_selectarcsegment(0, -7.6)
        femm.hi_setarcsegmentprop(1, "Ambiente", 0, 4, "<None>")
        femm.hi_clearselected()

        # COMENTADO PARA SETAR O QUE FOI POSTO EM CIMA
        # femm.hi_selectarcsegment(5, 5.3)  # o q é
        # femm.hi_setarcsegmentprop(1, "Ambiente", 0, 4, "<None>")  # parte de fora
        # femm.hi_clearselected()
        # progresso += 4.54
        # self.save_progress_simulation(progresso)
        #
        # # adicionar a tempera ambiente
        # write_log("-Setando temperatura 2")
        # femm.hi_selectarcsegment(5, -5.3)
        # femm.hi_setarcsegmentprop(1, "Ambiente", 0, 4, "<None>")  # parte de fora
        # femm.hi_clearselected()
        # progresso += 4.54
        # self.save_progress_simulation(progresso)
        #
        # # adicionar a tempera ambiente
        # write_log("-Setando temperatura 3")
        # femm.hi_selectarcsegment(-5, -5.3)
        # femm.hi_setarcsegmentprop(1, "Ambiente", 0, 4, "<None>")  # parte de fora
        # femm.hi_clearselected()
        # progresso += 4.54
        # self.save_progress_simulation(progresso)
        #
        # # adicionar a tempera ambiente
        # write_log("-Setando temperatura 4")
        # femm.hi_selectarcsegment(-5, 5.3)
        # femm.hi_setarcsegmentprop(1, "Ambiente", 0, 4, "<None>")  # parte de fora
        # femm.hi_clearselected()
        # progresso += 4.54
        # self.save_progress_simulation(progresso)

        # Salvar e Resolver
        write_log("-Salvando arquivo temp")
        femm.hi_zoomnatural()
        femm.hi_saveas(f"./{self.femm_generate_files}/term_atual" + str(self.index_simulacao) + ".feh")  # result termico
        femm.hi_analyze(1)
        femm.hi_loadsolution()
        progresso += 4.54
        self.save_progress_simulation(progresso)

        write_log("-Gerando imagens T e Térmico")
        femm.ho_showdensityplot(1, 0, 0, 400, 600)
        femm.ho_savebitmap(f"./{self.folder_name}/T{self.index_simulacao}.png")
        femm.ho_savebitmap(f'./{self.folder_name}/TERMICO.png')
        femm.ho_hidedensityplot()
        progresso += 4.54
        self.save_progress_simulation(progresso)

        # pulo do gato, aqui ocorre o acoplamento
        md_testator = 0
        md_condestator = 0
        # Calculando condutividade dos enrolamentos do estator
        a_cu = 0.0040
        ro_cu = 1 / (58 * 1000000)
        t1 = 5
        aux = 0
        self.cond_est.clear()
        self.t_estator.clear()
        write_log("-Calculando condutividade dos enrolamentos do estator")
        for j in range(1, 37):
            m = (j - 1) * 10
            self.theta1 = t1 + m
            x1 = 5.3278 * math.cos(self.theta1 * self.degrau)
            y1 = 5.3278 * math.sin(self.theta1 * self.degrau)
            #x1 = 48 * math.cos(self.theta1 * self.degrau)
            #y1 = 48 * math.sin(self.theta1 * self.degrau)
            femm.ho_seteditmode('area')
            femm.ho_selectblock(x1, y1)

            #print(f"x1: {x1} | y1: {y1}")

            aux3 = femm.ho_blockintegral(0)
            aux2 = aux3[0]
            self.t_estator.append(aux2)
            femm.ho_clearblock()
            aux = 1 / (1000000 * (ro_cu * (1 + a_cu * (aux2 - 300))))
            self.cond_est.append(aux)

            md_testator = md_testator + aux2
            md_condestator = md_condestator + aux
            progresso += 0.12
            self.save_progress_simulation(progresso)

        progresso += 4.54
        self.save_progress_simulation(progresso)

        md_testator = md_testator / 36
        md_condestator = md_condestator / 36

        self.temperatura_enr_estator.append(md_testator)
        self.cond_enr_estator.append(md_condestator)

        # Calculando condutividade dos enrolamentos do rotor
        a_al = 0.0040
        ro_al = 1 / (34.45 * 1000000)
        self.theta2 = 0
        md_trotor = 0
        self.t_rotor.clear()
        self.cond_rotor.clear()
        md_condrotor = 0
        write_log("-Calculando condutividade dos enrolamentos do rotor")
        for j in range(0, 27):
            self.theta2 = 12.86 * j
            x3 = 3.6923 * math.cos(self.theta2 * self.degrau)
            y3 = 3.6923 * math.sin(self.theta2 * self.degrau)
            #x3 = 33 * math.cos(self.theta2 * self.degrau)
            #y3 = 33 * math.sin(self.theta2 * self.degrau)
            femm.ho_seteditmode('area')
            femm.ho_selectblock(x3, y3)
            aux3 = femm.ho_blockintegral(0)
            aux2 = aux3[0]
            self.t_rotor.append(aux2)
            femm.ho_clearblock()
            aux = 1 / (1000000 * (ro_al * (1 + a_al * (aux2 - 300))))
            self.cond_rotor.append(aux)

            md_condrotor = md_condrotor + aux
            md_trotor = md_trotor + aux2
            progresso += 0.16
            self.save_progress_simulation(progresso)

        progresso += 4.54
        self.save_progress_simulation(progresso)

        self.temperatura_enr_rotor.append(md_trotor / 28)
        self.cond_enr_rotor.append(md_condrotor / 28)

        femm.ho_close()
        femm.hi_close()
        femm.closefemm()

        # salvar os parametros simulados no arquivo csv
        write_log("-Salvando arquivos e fechando simulação")
        data = {'Rotor Temp': self.temperatura_enr_rotor, 'Stator Temp': self.temperatura_enr_estator,
                'Conductivity Rotor': self.cond_enr_rotor, 'Conductivity Stator': self.cond_enr_estator}
        df1 = pd.DataFrame(data=data)
        df1.to_csv(f'./{self.femm_generate_files}/Resultados.csv')

        df2 = np.asarray(self.p_rotor)
        np.savetxt(f"./{self.femm_generate_files}/" + "protor" + str(self.index_simulacao) + ".csv", df2,
                   delimiter=",")

        df3 = np.asarray(self.p_estator)
        np.savetxt(f"./{self.femm_generate_files}/" + "p_estator" + str(self.index_simulacao) + ".csv", df3, delimiter=",")

        self.p_rotor.clear()
        self.p_estator.clear()

        self.save_data()
        progresso += 4.54
        self.save_progress_simulation(progresso)

    def iniciar_femm_original(self):

        femm.openfemm()
        if self.primeira_simulacao:
            femm.opendocument(f'./{self.femm_files}/MOTOR.fem')
            femm.mi_saveas(f'./{self.femm_files}/temp.fem')
            self.criando_materiais()
        else:
            femm.opendocument(f'./{self.femm_files}/temp.fem')
            for j in range(36):
                femm.mi_modifymaterial('Copper_' + str(j) + '_estator', 5, self.cond_est[j])

            femm.mi_modifymaterial('Aluminio_rotor', 5, self.cond_enr_rotor[self.index_simulacao - 2])

        self.cond_est.clear()  # zera a self.cond_est

        # Atualização dos materiais dos enrolamentos de cobre
        t1 = 5
        for j in range(1, 37):
            k = j - 1
            m = k * 10
            self.theta1 = t1 + m
            x1 = 48 * math.cos(self.theta1 * self.degrau)
            y1 = 48 * math.sin(self.theta1 * self.degrau)
            # x1 = 5.3278 * math.cos(self.theta1 * self.degrau)
            # y1 = 5.3278 * math.sin(self.theta1 * self.degrau)
            #print(x1)
            #print(y1)
            femm.mi_selectlabel(x1, y1)
            # diz qual o sentido do enrolamento
            # o que é ess 44
            # A member of group number group, The number of turns associated with this label is denoted by turns.
            if (k >= 0 and k <= 2) or (k >= 18 and k <= 20):
                femm.mi_setblockprop('Copper_' + str(k) + '_estator', 1, 0, 'C', 0, 1, 44)
                femm.mi_clearselected()
            elif (k >= 3 and k <= 5) or (k >= 21 and k <= 23):
                femm.mi_setblockprop('Copper_' + str(k) + '_estator', 1, 0, 'A', 0, 1, -44)
                femm.mi_clearselected()
            elif (k >= 6 and k <= 8) or (k >= 24 and k <= 26):
                femm.mi_setblockprop('Copper_' + str(k) + '_estator', 1, 0, 'B', 0, 1, 44)
                femm.mi_clearselected()
            elif (k >= 9 and k <= 11) or (k >= 27 and k <= 29):
                femm.mi_setblockprop('Copper_' + str(k) + '_estator', 1, 0, 'C', 0, 1, -44)
                femm.mi_clearselected()
            elif (k >= 12 and k <= 14) or (k >= 30 and k <= 32):
                femm.mi_setblockprop('Copper_' + str(k) + '_estator', 1, 0, 'A', 0, 1, 44)
                femm.mi_clearselected()
            elif (k >= 15 and k <= 17) or (k >= 33 and k <= 35):
                femm.mi_setblockprop('Copper_' + str(k) + '_estator', 1, 0, 'B', 0, 1, -44)
                femm.mi_clearselected()
            femm.mi_clearselected()

        # Atualização dos materiais dos enrolamentos do motor
        self.theta2 = 0
        for k in range(28):
            self.theta2 = 12.86 * k
            # x3 = 3.6923 * math.cos(self.theta2 * self.degrau)
            # y3 = 3.6923 * math.sin(self.theta2 * self.degrau)
            x3 = 33 * math.cos(self.theta2 * self.degrau)
            y3 = 33 * math.sin(self.theta2 * self.degrau)
            #print(x3)
            #print(y3)
            femm.mi_selectlabel(x3, y3)
            femm.mi_setblockprop('Aluminio_rotor', 1, 0, '<None>', 0, 1, 1)
            femm.mi_clearselected()

        # Modificando o parâmetro de corrente do circuito
        femm.mi_modifycircprop('A', 1, self.correnteA)
        femm.mi_modifycircprop('B', 1, self.correnteB)
        femm.mi_modifycircprop('C', 1, self.correnteC)
        #print(self.correnteA)
        #print(self.correnteB)
        #print(self.correnteC)
        # Solucionando o problema
        femm.mi_zoomnatural()
        femm.mi_saveas('temp.fem')
        femm.smartmesh(1)  # malha pronta
        femm.mi_analyze(1)

        femm.mi_loadsolution()  # carrega e exibe a solução correspondente à geometria atual
        femm.mo_showdensityplot(1, 0, 0, 2.774, 'mag')  # Verificar como fica a distribuição de campo
        femm.mo_savebitmap('M' + str(self.index_simulacao) + '.png')  # salva o resultado em imagem
        femm.mi_saveas('./MAG' + str(60) + str(self.index_simulacao) + '.fem')
        femm.mo_hidedensityplot()

        # Perdas resistivas no enrolamento do estator
        m_estator = 0  # t1 = ângulo inicial do estator
        # Lendo perdas no estator
        for j in range(1, 37):
            m = (j - 1) * 10
            self.theta1 = t1 + m
            x1 = 48 * math.cos(self.theta1 * self.degrau)
            y1 = 48 * math.sin(self.theta1 * self.degrau)
            # x1 = 5.3278 * math.cos(self.theta1 * self.degrau)
            # y1 = 5.3278 * math.sin(self.theta1 * self.degrau)
            #print(x1)
            #print(y1)
            femm.mo_seteditmode('area')  #
            femm.mo_selectblock(x1, y1)
            aux = femm.mo_blockintegral(4)
            #print(aux)
            femm.mo_clearblock()
            self.p_estator.append(aux)
            m_estator = m_estator + aux

        m_estator = m_estator / 36
        #print(m_estator)
        self.media_enr_estator.append(m_estator)

        # Perdas nos enrolamentos do rotor
        m_rotor = 0
        # Lendo as perdas no rotor
        for j in range(0, 28):
            self.theta2 = 12.86 * j
            x3 = 33 * math.cos(self.theta2 * self.degrau)
            y3 = 33 * math.sin(self.theta2 * self.degrau)
            # x3 = 3.6923 * math.cos(self.theta2 * self.degrau)
            # y3 = 3.6923 * math.sin(self.theta2 * self.degrau)
            femm.mo_seteditmode('area')
            femm.mo_selectblock(x3, y3)
            aux = femm.mo_blockintegral(6)
            femm.mo_clearblock()
            self.p_rotor.append(aux)
            m_rotor = m_rotor + aux

        m_rotor = m_rotor / 28  # Valores das barras da gaiola do rotor
        #print(m_rotor)
        self.media_enr_rotor.append(m_rotor)

        # Perdas no estator
        femm.mo_seteditmode('area')
        femm.mo_selectblock(60, 0)
        self.pestator.append(femm.mo_blockintegral(6))
        femm.mo_clearblock()

        # Perdas no rotor
        femm.mo_seteditmode('area')
        femm.mo_selectblock(18, 0)
        self.protor.append(femm.mo_blockintegral(6))
        femm.mo_clearblock()

        femm.mo_close()
        femm.mi_close()

        ################################################
        # Simulação Térmica
        ################################################

        femm.opendocument('./TERMICO.feh')
        femm.hi_saveas('./term_atual.feh')

        femm.hi_probdef('centimeters', 'planar', 1E-8, 30, 30)
        femm.hi_addboundprop("Heat flux", 1, 0, 278000, 0, 0, 0)
        femm.hi_addboundprop("Heat flux1", 1, 0, 0, 0, 0, 0)
        femm.hi_addboundprop("Convection", 2, 0, 0, 300, 30, 0)

        # INSERINDO CONDIÇÃO DE CONTORNO REFERENTE ÀS PERDAS NOS ENROLAMENTOS DO ESTATOR

        #print(self.p_estator)
        # na proxima colocar um comparador da temp interna
        t1 = 5
        for j in range(36):
            m = j * 10
            self.theta1 = t1 + m

            femm.hi_addconductorprop("Enr_" + str(j) + "_Estator", 0, self.p_estator[j], 0)

            femm.hi_selectarcsegment(5.7692 * math.cos((self.theta1 + 2) * self.degrau),
                                     5.7692 * math.sin((self.theta1 + 2) * self.degrau))  # Superior 1
            femm.hi_setarcsegmentprop(1, "Heat flux", 0, 4, "Enr_" + str(j) + "_Estator")  # pq é 4?
            femm.hi_clearselected()

            femm.hi_selectarcsegment(5.8846 * math.cos((self.theta1 + 0.4) * self.degrau),
                                     5.8846 * math.sin((self.theta1 + 0.4) * self.degrau))  # Superior 2
            femm.hi_setarcsegmentprop(1, "Heat flux", 0, 4, "Enr_" + str(j) + "_Estator")
            femm.hi_clearselected()

            femm.hi_selectarcsegment(5.8846 * math.cos((self.theta1 - 0.4) * self.degrau),
                                     5.8846 * math.sin((self.theta1 - 0.4) * self.degrau))  # Superior 3
            femm.hi_setarcsegmentprop(1, "Heat flux", 0, 4, "Enr_" + str(j) + "_Estator")
            femm.hi_clearselected()

            femm.hi_selectarcsegment(5.7692 * math.cos((self.theta1 - 2) * self.degrau),
                                     5.7692 * math.sin((self.theta1 - 2) * self.degrau))  # Superior 4
            femm.hi_setarcsegmentprop(1, "Heat flux", 0, 4, "Enr_" + str(j) + "_Estator")
            femm.hi_clearselected()

            femm.hi_selectarcsegment(5 * math.cos((self.theta1 + 0.5) * self.degrau),
                                     5 * math.sin((self.theta1 + 0.5) * self.degrau))  # Inferior 1
            femm.hi_setarcsegmentprop(1, "Heat flux", 0, 4, "Enr_" + str(j) + "_Estator")
            femm.hi_clearselected()

            femm.hi_selectarcsegment(5 * math.cos((self.theta1 - 0.5) * self.degrau),
                                     5 * math.sin((self.theta1 - 0.5) * self.degrau))  # Inferior 2
            femm.hi_setarcsegmentprop(1, "Heat flux", 0, 4, "Enr_" + str(j) + "_Estator")
            femm.hi_clearselected()

            femm.hi_selectsegment(4.8 * math.cos((self.theta1 + 0.3) * self.degrau),
                                  4.8 * math.sin((self.theta1 + 0.3) * self.degrau))  # Inferior 3
            femm.hi_setarcsegmentprop(1, "Heat flux", 0, 4, "Enr_" + str(j) + "_Estator")
            femm.hi_clearselected()

            femm.hi_selectsegment(5.3278 * math.cos((self.theta1 + 0.3) * self.degrau),
                                  5.3278 * math.sin((self.theta1 + 0.3) * self.degrau))  # Lado 1
            femm.hi_setarcsegmentprop(1, "Heat flux", 0, 4, "Enr_" + str(j) + "_Estator")
            femm.hi_clearselected()

            femm.hi_selectsegment(5.3278 * math.cos((self.theta1 - 0.3) * self.degrau),
                                  5.3278 * math.sin((self.theta1 - 0.3) * self.degrau))  # Lado 2
            femm.hi_setarcsegmentprop(1, "Heat flux", 0, 4, "Enr_" + str(j) + "_Estator")
            femm.hi_clearselected()
        # self.p_estator.clear()
        self.theta3 = 0
        for j in range(28):
            self.theta3 = 12.86 * j
            x3 = 3.6923 * math.cos(self.theta3 * self.degrau)
            y3 = 3.6923 * math.sin(self.theta3 * self.degrau)

            femm.hi_addconductorprop("Enr_" + str(j) + "_Rotor", 0, self.p_rotor[j], 0)

            femm.hi_selectarcsegment(3.6923 * math.cos((self.theta3 + 2) * self.degrau),
                                     3.6923 * math.sin((self.theta3 + 2) * self.degrau))  # arco superior 1
            femm.hi_setarcsegmentprop(1, "Heat flux1 ", 0, 4, "Enr_" + str(j) + "_Rotor")
            femm.hi_clearselected()

            femm.hi_selectarcsegment(3.6923 * math.cos((self.theta3 - 2) * self.degrau),
                                     3.6923 * math.sin((self.theta3 - 2) * self.degrau))  # arco superior 2
            femm.hi_setarcsegmentprop(1, "Heat flux1 ", 0, 4, "Enr_" + str(j) + "_Rotor")
            femm.hi_clearselected()

            femm.hi_selectsegment(4.5 * math.cos((self.theta3 + 0.2) * self.degrau),
                                  4.5 * math.sin((self.theta3 + 0.2) * self.degrau))  # segmento superior 1
            femm.hi_setarcsegmentprop(1, "Heat flux1 ", 0, 4, "Enr_" + str(j) + "_Rotor")
            femm.hi_clearselected()

            femm.hi_selectsegment(4.5 * math.cos((self.theta3 - 0.2) * self.degrau),
                                  4.5 * math.sin((self.theta3 - 0.2) * self.degrau))  # segmento superior 2
            femm.hi_setarcsegmentprop(1, "Heat flux1 ", 0, 4, "Enr_" + str(j) + "_Rotor")
            femm.hi_clearselected()

            femm.hi_selectsegment(3.6923 * math.cos((self.theta3 - 1) * self.degrau),
                                  3.6923 * math.sin((self.theta3 - 1) * self.degrau))  # segmento lado 1
            femm.hi_setarcsegmentprop(1, "Heat flux1 ", 0, 4, "Enr_" + str(j) + "_Rotor")
            femm.hi_clearselected()

            femm.hi_selectsegment(3.6923 * math.cos((self.theta3 + 1) * self.degrau),
                                  3.6923 * math.sin((self.theta3 + 1) * self.degrau))  # segmento lado 2
            femm.hi_setarcsegmentprop(1, "Heat flux1 ", 0, 4, "Enr_" + str(j) + "_Rotor")
            femm.hi_clearselected()

            femm.hi_selectarcsegment(2.93 * math.cos((self.theta3 + 0.2) * self.degrau),
                                     2.93 * math.sin((self.theta3 + 0.2) * self.degrau))  # arco inferior 1
            femm.hi_setarcsegmentprop(1, "Heat flux1 ", 0, 4, "Enr_" + str(j) + "_Rotor")
            femm.hi_clearselected()

            femm.hi_selectarcsegment(2.93 * math.cos((self.theta3 - 0.2) * self.degrau),
                                     2.93 * math.sin((self.theta3 - 0.2) * self.degrau))  # arco inferior 2
            femm.hi_setarcsegmentprop(1, "Heat flux1 ", 0, 4, "Enr_" + str(j) + "_Rotor")
            femm.hi_clearselected()
        # self.p_rotor.clear()

        femm.hi_addconductorprop("Perdas_" + str(self.index_simulacao - 1) + "_Estator", 0,
                                 self.pestator[self.index_simulacao - 1], 0)
        femm.hi_addboundprop("Ambiente", 2, 0, 0, 300, 52, 0)
        # adicionar a temperatura ambiente
        # Perdas no ferro do estator
        femm.hi_selectarcsegment(5, 5.3)  # o q é
        femm.hi_setarcsegmentprop(1, "Ambiente", 0, 4, "<None>")  # parte de fora
        femm.hi_clearselected()
        # adicionar a tempera ambiente
        femm.hi_selectarcsegment(5, -5.3)
        femm.hi_setarcsegmentprop(1, "Ambiente", 0, 4, "<None>")  # parte de fora
        femm.hi_clearselected()
        # adicionar a tempera ambiente
        femm.hi_selectarcsegment(-5, -5.3)
        femm.hi_setarcsegmentprop(1, "Ambiente", 0, 4, "<None>")  # parte de fora
        femm.hi_clearselected()
        # adicionar a tempera ambiente
        femm.hi_selectarcsegment(-5, 5.3)
        femm.hi_setarcsegmentprop(1, "Ambiente", 0, 4, "<None>")  # parte de fora
        femm.hi_clearselected()

        # Salvar e Resolver
        femm.hi_zoomnatural()
        femm.hi_saveas("./term_atual" + str(self.index_simulacao) + ".feh")  # result termico
        femm.hi_analyze(1)
        femm.hi_loadsolution()

        femm.ho_showdensityplot(1, 0, 0, 200, 400)
        femm.ho_savebitmap("./" + "T" + str(self.index_simulacao) + ".png")
        femm.ho_savebitmap('./TERMICO.png')
        femm.ho_hidedensityplot()

        # pulo do gato, aqui ocorre o acoplamento
        md_testator = 0
        md_condestator = 0
        # Calculando condutividade dos enrolamentos do estator
        a_cu = 0.0040
        ro_cu = 1 / (58 * 1000000)
        t1 = 5
        aux = 0
        self.cond_est.clear()
        self.t_estator.clear()
        for j in range(1, 37):
            m = (j - 1) * 10
            self.theta1 = t1 + m

            x1 = 48 * math.cos(self.theta1 * self.degrau)
            y1 = 48 * math.sin(self.theta1 * self.degrau)

            femm.ho_seteditmode('area')
            femm.ho_selectblock(x1, y1)
            aux3 = femm.ho_blockintegral(0)
            aux2 = aux3[0]
            self.t_estator.append(aux2)
            femm.ho_clearblock()
            aux = 1 / (1000000 * (ro_cu * (1 + a_cu * (aux2 - 300))))
            self.cond_est.append(aux)

            md_testator = md_testator + aux2
            md_condestator = md_condestator + aux

        md_testator = md_testator / 36
        md_condestator = md_condestator / 36

        self.temperatura_enr_estator.append(md_testator)
        self.cond_enr_estator.append(md_condestator)

        # Calculando condutividade dos enrolamentos do rotor
        a_al = 0.0040
        ro_al = 1 / (34.45 * 1000000)
        self.theta2 = 0
        md_trotor = 0
        self.t_rotor.clear()
        self.cond_rotor.clear()
        md_condrotor = 0
        for j in range(0, 27):
            self.theta2 = 12.86 * j

            x3 = 33 * math.cos(self.theta2 * self.degrau)
            y3 = 33 * math.sin(self.theta2 * self.degrau)

            femm.ho_seteditmode('area')
            femm.ho_selectblock(x3, y3)
            aux3 = femm.ho_blockintegral(0)
            aux2 = aux3[0]
            self.t_rotor.append(aux2)
            femm.ho_clearblock()
            aux = 1 / (1000000 * (ro_al * (1 + a_al * (aux2 - 300))))
            self.cond_rotor.append(aux)

            md_condrotor = md_condrotor + aux
            md_trotor = md_trotor + aux2

        self.temperatura_enr_rotor.append(md_trotor / 28)
        self.cond_enr_rotor.append(md_condrotor / 28)

        femm.ho_close()
        femm.hi_close()
        femm.closefemm()

        # salvar os parametros simulados no arquivo csv

        data = {'Rotor Temp': self.temperatura_enr_rotor, 'Stator Temp': self.temperatura_enr_estator,
                'Conductivity Rotor': self.cond_enr_rotor, 'Conductivity Stator': self.cond_enr_estator}
        df1 = pd.DataFrame(data=data)
        df1.to_csv('./Resultados.csv')

        df2 = np.asarray(self.p_rotor)
        np.savetxt("./" + "protor" + str(self.index_simulacao) + ".csv", df2,
                   delimiter=",")

        df3 = np.asarray(self.p_estator)
        np.savetxt("./" + "p_estator" + str(self.index_simulacao) + ".csv", df3, delimiter=",")

        self.p_rotor.clear()
        self.p_estator.clear()
# Para testar simulações

# dados_teste= {
#         0:{"A": 2.5, "B": 2.5, "C": 2.5},
#         1:{"A": 3.7, "B": 3.7, "C": 3.75},
#         2:{"A": 4, "B": 4.1, "C": 4},
#         3:{"A": 4.4, "B": 4.3, "C": 4.4},
#     }
# femm_simulacao = FEMMSimulationController()
# femm_simulacao.set_femm_atributes(ca=dados_teste[0]["A"], cb=dados_teste[0]["B"], cc=dados_teste[0]["C"],
#                                      index=0,
#                                      first=True,
#                                      folder_name="TesteFEMM")
#
# femm_simulacao.iniciar_femm()
# for teste in dados_teste:
#      femm_simulacao.set_femm_atributes(dados_teste[teste]["A"], dados_teste[teste]["B"], dados_teste[teste]["C"],teste,teste==0,teste)
#      femm_simulacao.iniciar_femm()

