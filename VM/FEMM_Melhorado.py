import femm
import math
import numpy as np
import pandas  # openpy

# Declaração de vetores
CORRENTE_A = []
CORRENTE_B = []
CORRENTE_C = []

I = []

p_estator = []
degrau = math.pi / 180.0
media_enr_estator = []
media_enr_rotor = []

p_rotor = []
pestator = []
protor = []
t_estator = []

cond_est = []
cond_rotor = []

temperatura_enr_estator = []
cond_enr_estator = []
t_rotor = []
temperatura_enr_rotor = []
cond_enr_rotor = []
torques = []


df_corrente = pandas.read_excel('Planilha_Simulação.xlsx', sheet_name='RMS')
df = pandas.DataFrame(df_corrente)

#len serve pra dizer a quantidade do q ta sendo lido
for l in range(len(df_corrente)):
    a = df_corrente._get_value(l, 'Fase_A') # armazena o valor da corrente em p
    b = df_corrente._get_value(l, 'Fase_B')  # armazena o valor da corrente em p
    c = df_corrente._get_value(l, 'Fase_C')  # armazena o valor da corrente em p
    b = -1*b/2
    c = -1*c/2
    CORRENTE_A.append(a)  # Adiciono os valores de corrente dos sensores
    CORRENTE_B.append(b)  # rms
    CORRENTE_C.append(c)  # so a parte real

# Função para obter o último ID da tabela
def ultimo_id():
    return len(df_corrente)  # len é pra saber o q tem de informação no df_corrente


# Função para criar materiais SIMULAÇÃO MAGNETICA
def criando_materiais():
    # Cobre para o estator
    for j in range(36):  # faz isso pras 36 ranhuras do motor
        # nome do material, Permeabilidade relativa em x e y,0,0, condutividade eletrica,0,0,volume do ferro,
        # fio magnético,Número de fios na construção do fio, Diâmetro de cada fio constituinte do fio em milímetros.
        femm.mi_addmaterial('Copper_' + str(j) + '_estator', 1, 1, 0, 0, 58, 0, 0, 1, 3, 0, 0, 1, 0.45466985972222)
        # Alumínio para o rotor
    femm.mi_addmaterial('Aluminio_rotor', 1, 1, 0, 0, 34.45, 0, 0, 1, 3, 0, 0, 1, 1)
    femm.mi_getmaterial("Pure Iron") #pega um material da biblioteca do femm
    femm.mi_getmaterial("Air") #precisa colocar o nome correto
    femm.mi_getmaterial("M-45 Steel")

def criando_materiais_Estator():
    #ranhuras
    t1 = 5
    for j in range(36):
        k = j - 1
        m = k * 10
        theta1 = t1 + m
        x1 = 5.3278 * math.cos(theta1 * degrau)
        y1 = 5.3278 * math.sin(theta1 * degrau)
        femm.mi_addblocklabel(x1, y1)
        femm.mi_selectlabel(x1, y1)
        femm.mi_setblockprop('Copper_' + str(j) + '_estator', 1, 0, '', 1, 1)
        femm.mi_clearselected()
    #nucleo
    x2 = 0
    y2 = 6.59
    femm.mi_addblocklabel(x2, y2) #Cria o ponto que receberá o material
    femm.mi_selectlabel(x2, y2) #Seleciona o ponto criado
    femm.mi_setblockprop('M-45 Steel', 1, 0, '<None>', 0, 1, 1) #Define o material do ponto
    femm.mi_clearselected() # limpa a seleção, sempre colocar ele


def criando_materiais_Rotor():
   #Ranhuras
    theta2 = 0
    for k in range(28):
        theta2 = 12.86 * k
        x3 = 3.6923 * math.cos(theta2 * degrau)
        y3 = 3.6923 * math.sin(theta2 * degrau)
        femm.mi_addblocklabel(x3,y3)
        femm.mi_selectlabel(x3,y3)
        femm.mi_setblockprop('Aluminio_rotor', 1, 0, '<None>', 0, 1, 1)
        femm.mi_clearselected()
    #Nucleo
    x4 = 2
    y4 = 1.59
    femm.mi_addblocklabel(x4, y4)  # Cria o ponto que receberá o material
    femm.mi_selectlabel(x4, y4)  # Seleciona o ponto criado
    femm.mi_setblockprop('M-45 Steel', 1, 0, '<None>', 0, 1, 1)  # Define o material do ponto
    femm.mi_clearselected()  # limpa a seleção, sempre colocar ele
    x5 = 0
    y5 = 0
    femm.mi_addblocklabel(x5, y5)  # Cria o ponto que receberá o material
    femm.mi_selectlabel(x5, y5)  # Seleciona o ponto criado
    femm.mi_setblockprop('M-45 Steel', 1, 0, '<None>', 0, 1, 1) # Define o material do ponto
    femm.mi_clearselected()  # limpa a seleção, sempre colocar ele


def criando_materiais_externo():
    #Camisa
    x6 =0
    y6 =8.3
    femm.mi_addblocklabel(x6, y6)# Cria o ponto que receberá o material
    femm.mi_selectlabel(x6, y6)# Seleciona o ponto criado
    femm.mi_setblockprop('Pure Iron', 1, 0, '<None>', 0, 1, 1)# Define o material do ponto
    femm.mi_clearselected() # limpa a seleção, sempre colocar ele
   #entreferro
    x7 = 0
    y7 = 4.62
    femm.mi_addblocklabel(x7, y7)  # Cria o ponto que receberá o material
    femm.mi_selectlabel(x7, y7)  # Seleciona o ponto criado
    femm.mi_setblockprop('Air', 1, 0, '<None>', 0, 1, 1)  # Define o material do ponto
    femm.mi_clearselected()  # limpa a seleção, sempre colocar ele
    #ambiente
    x8 = 0
    y8 = 10
    femm.mi_addblocklabel(x8, y8)  # Cria o ponto que receberá o material
    femm.mi_selectlabel(x8, y8)  # Seleciona o ponto criado
    femm.mi_setblockprop('Air', 1, 0, '<None>', 0, 1, 1)  # Define o material do ponto
    femm.mi_clearselected()  # limpa a seleção, sempre colocar ele

def criando_circuito():
    femm.mi_addcircprop("A", 0, 1)
    femm.mi_addcircprop("B", 0, 1)
    femm.mi_addcircprop("C", 0, 1)

# Função para criar materiais SIMULAÇÃO TERMICA
def criando_materiais_TERMICA():
    femm.hi_getmaterial("Copper, Pure") #pega um material da biblioteca do femm
    femm.hi_getmaterial("Air") #precisa colocar o nome correto
    femm.hi_getmaterial("Aluminum, Pure")
    femm.hi_getmaterial("Iron, Pure")
    femm.hi_addmaterial("Núcleo", 23, 23, 0, 3)

#fazer os outros materias
def criando_materiais_Estator_TERMICA():
    #ranhuras
    t1 = 5
    for j in range(36):
        k = j - 1
        m = k * 10
        theta1 = t1 + m
        x10 = 5.3278 * math.cos(theta1 * degrau)
        y10 = 5.3278 * math.sin(theta1 * degrau)
        femm.hi_addblocklabel(x10, y10)
        femm.hi_selectlabel(x10, y10)
        femm.hi_setblockprop('Copper, Pure', 1, 1, 1)
        femm.hi_clearselected()
    #nucleo
    x20 = 0
    y20 = 6.59
    femm.hi_addblocklabel(x20, y20) #Cria o ponto que receberá o material
    femm.hi_selectlabel(x20, y20) #Seleciona o ponto criado
    femm.hi_setblockprop('Núcleo',1, 1, 1) #Define o material do ponto
    femm.hi_clearselected() # limpa a seleção, sempre colocar ele Conitar a


def criando_materiais_Rotor_TERMICA():
   #Ranhuras
    theta2 = 0
    for k in range(28):
        theta2 = 12.86 * k
        x30 = 3.6923 * math.cos(theta2 * degrau)
        y30 = 3.6923 * math.sin(theta2 * degrau)
        femm.hi_addblocklabel(x30,y30)
        femm.hi_selectlabel(x30,y30)
        femm.hi_setblockprop('Aluminum, Pure', 1, 1, 1)
        femm.hi_clearselected()
    #Nucleo
    x40 = 2
    y40 = 1.59
    femm.hi_addblocklabel(x40, y40)  # Cria o ponto que receberá o material
    femm.hi_selectlabel(x40, y40)  # Seleciona o ponto criado
    femm.hi_setblockprop('Núcleo', 1, 1, 1)  # Define o material do ponto
    femm.hi_clearselected()  # limpa a seleção, sempre colocar ele
    x50 = 0
    y50 = 0
    femm.hi_addblocklabel(x50, y50)  # Cria o ponto que receberá o material
    femm.hi_selectlabel(x50, y50)  # Seleciona o ponto criado
    femm.hi_setblockprop('Núcleo', 1, 1, 1) # Define o material do ponto
    femm.hi_clearselected()  # limpa a seleção, sempre colocar ele


def criando_materiais_externo_TERMICA():
    #Camisa
    x60 =0
    y60 =8.3
    femm.hi_addblocklabel(x60, y60)# Cria o ponto que receberá o material
    femm.hi_selectlabel(x60, y60)# Seleciona o ponto criado
    femm.hi_setblockprop('Iron, Pure', 1, 1, 1)# Define o material do ponto
    femm.hi_clearselected() # limpa a seleção, sempre colocar ele
   #entreferro
    x70 = 0
    y70 = 4.62
    femm.hi_addblocklabel(x70, y70)  # Cria o ponto que receberá o material
    femm.hi_selectlabel(x70, y70)  # Seleciona o ponto criado
    femm.hi_setblockprop('Air', 1, 1, 1)  # VERIFICAR SE TÁ CERTO ESSE FATOR
    femm.hi_clearselected()  # limpa a seleção, sempre colocar ele
    #ambiente
    x80 = 0
    y80 = 10
    femm.hi_addblocklabel(x80, y80)  # Cria o ponto que receberá o material
    femm.hi_selectlabel(x80, y80)  # Seleciona o ponto criado
    femm.hi_setblockprop('Air', 1, 1, 1)  # Define o material do ponto
    femm.hi_clearselected()  # limpa a seleção, sempre colocar ele



controle = True
id_final = ultimo_id()

first_id = df_corrente.sort_values(by='N', ascending=True)
first_id = first_id.head(6)
for id in first_id:
    i = (first_id['N'].iloc[0])


print(i)

print("Correntes A: ", CORRENTE_A)
print("Correntes B: ", CORRENTE_B)
print("Correntes C: ", CORRENTE_C)
while controle:
    I.append(i)

    femm.openfemm()

    if i == 1:  # se I == 1 é a primeira simulação
        femm.opendocument('./femm_files/Motor_Teste1.fem')
        femm.mi_saveas('temp.fem')
        criando_materiais()
        criando_materiais_Rotor()
        criando_materiais_Estator()
        criando_materiais_externo()
        criando_circuito()

    else:  # sen for a primeira simulação, fazer isso
        femm.opendocument('temp.fem')
        for j in range(36):
            femm.mi_modifymaterial('Copper_' + str(j) + '_estator', 5, cond_est[j])
        femm.mi_modifymaterial('Aluminio_rotor', 5, cond_enr_rotor[i - 2])

    cond_est.clear()  # zera a cond_est

    # Atualização dos materiais dos enrolamentos de cobre
    t1 = 5
    for j in range(1, 37):
        k = j - 1
        m = k * 10
        theta1 = t1 + m
        x1 = 5.3278 * math.cos(theta1 * degrau)
        y1 = 5.3278 * math.sin(theta1 * degrau)
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
    theta2 = 0
    for k in range(28):
        theta2 = 12.86 * k
        x3 = 3.6923 * math.cos(theta2 * degrau)
        y3 = 3.6923 * math.sin(theta2 * degrau)
        femm.mi_selectlabel(x3, y3)
        femm.mi_setblockprop('Aluminio_rotor', 1, 0, '<None>', 0, 1, 1)
        femm.mi_clearselected()

    # femm.mi_selectlabel(0, 8.3)
    # femm.mi_setblockprop('Pure Iron', 1, 0, '<None>', 0, 1, 1)
    # femm.mi_clearselected()
    # femm.mi_selectlabel(-0.3, 14.6)
    # femm.mi_setblockprop('Air', 1, 0, '<None>', 0, 1, 1)
    # femm.mi_clearselected()

    # Modificando o parâmetro de corrente do circuito
    femm.mi_modifycircprop('A', 1, CORRENTE_A[i - 1])  # verificar se no final n ta pegando o mesmo valor
    femm.mi_modifycircprop('B', 1, CORRENTE_B[i - 1])
    femm.mi_modifycircprop('C', 1, CORRENTE_C[i - 1])

    # Solucionando o problema
    # femm.mi_smartmesh(1)# malha pronta
    femm.mi_createmesh()  # cria a malha
    femm.mi_analyze(0)
    femm.mi_loadsolution()  # carrega e exibe a solução correspondente à geometria atual
    # femm.ho_shownames(0)
    # femm.ho_hidenames()

    femm.mo_showdensityplot(1, 0, 0, 2.0, 'mag')  # Verificar como fica a distribuição de campo
    femm.mo_savebitmap('M' + str(i) + '.bmp')  # salva o resultado em imagem
    femm.mo_hidedensityplot()
    femm.mi_zoomnatural()
    femm.mi_saveas('temp.fem')
    femm.mi_saveas('Resultados/MAG' + str(60) + str(i) + '.fem')

    # Cálculo do torque
    femm.mo_seteditmode('group')
    femm.mo_groupselectblock(2)  # Seleciona o grupo 2 (rotor)
    torque = femm.mo_blockintegral(22)
    torques.append(torque)

    # Perdas resistivas no enrolamento do estator
    m_estator = 0  # t1 = ângulo inicial do estator
    # Lendo perdas no estator
    for j in range(1, 37):
        m = (j - 1) * 10
        theta1 = t1 + m
        x1 = 5.3278 * math.cos(theta1 * degrau)
        y1 = 5.3278 * math.sin(theta1 * degrau)
        femm.mo_seteditmode('area')  #
        femm.mo_selectblock(x1, y1)
        aux = femm.mo_blockintegral(4)
        femm.mo_clearblock()
        p_estator.append(aux)
        m_estator = m_estator + aux

    m_estator = m_estator / 36
    media_enr_estator.append(m_estator)

    # Perdas nos enrolamentos do rotor
    m_rotor = 0
    # Lendo as perdas no rotor
    for j in range(0, 28):
        theta2 = 12.86 * j
        x3 = 3.6923 * math.cos(theta2 * degrau)
        y3 = 3.6923 * math.sin(theta2 * degrau)
        femm.mo_seteditmode('area')
        femm.mo_selectblock(x3, y3)
        aux = femm.mo_blockintegral(6)
        femm.mo_clearblock()
        p_rotor.append(aux)
        m_rotor = m_rotor + aux

    m_rotor = m_rotor / 28  # Valores das barras da gaiola do rotor
    media_enr_rotor.append(m_rotor)

    # Perdas no estator
    femm.mo_seteditmode('area')
    femm.mo_selectblock(6.6923, 0)  # 60
    pestator.append(femm.mo_blockintegral(6))
    femm.mo_clearblock()

    # Perdas no rotor
    femm.mo_seteditmode('area')
    femm.mo_selectblock(2.0769, 0)  # 18
    protor.append(femm.mo_blockintegral(6))
    femm.mo_clearblock()

    # femm.mo_close()
    # femm.mi_close()
    femm.closefemm()


    ################################################
    # Simulação Térmica
    ################################################
    femm.openfemm()
    femm.opendocument('Termico_Teste1.FEH')
    criando_materiais_TERMICA()
    criando_materiais_Estator_TERMICA()
    criando_materiais_Rotor_TERMICA()
    criando_materiais_externo_TERMICA()
    femm.hi_saveas('term_atual.feh')
    femm.hi_probdef('centimeters', 'planar', 1E-8, 30, 30)
    femm.hi_addboundprop("Heat flux", 1, 0, 278000, 0, 0, 0)  # qs densidade de fluxo de calor
    femm.hi_addboundprop("Heat flux1", 1, 0, 0, 0, 0, 0)
    femm.hi_addboundprop("Convection", 2, 0, 0, 300, 30, 0)  # transferência de calor desejada,temperatura externa
    # INSERINDO CONDIÇÃO DE CONTORNO REFERENTE ÀS PERDAS NOS ENROLAMENTOS DO ESTATOR
    print(p_estator)
    # na proxima colocar um comparador da temp interna
    t1 = 5
    for j in range(36):
        m = j * 10
        theta1 = t1 + m

        femm.hi_addconductorprop("Enr_" + str(j) + "_Estator", 0, p_estator[j], 0)

        femm.hi_selectarcsegment(5.7692 * math.cos((theta1 + 2) * degrau),
                                 5.7692 * math.sin((theta1 + 2) * degrau))  # Superior 1
        femm.hi_setarcsegmentprop(1, "Heat flux", 0, 1, "Enr_" + str(j) + "_Estator")
        femm.hi_clearselected()

        femm.hi_selectarcsegment(5.8846 * math.cos((theta1 + 0.4) * degrau),
                                 5.8846 * math.sin((theta1 + 0.4) * degrau))  # Superior 2
        femm.hi_setarcsegmentprop(1, "Heat flux", 0, 2, "Enr_" + str(j) + "_Estator")
        femm.hi_clearselected()

        femm.hi_selectarcsegment(5.8846 * math.cos((theta1 - 0.4) * degrau),
                                 5.8846 * math.sin((theta1 - 0.4) * degrau))  # Superior 3
        femm.hi_setarcsegmentprop(1, "Heat flux", 0, 3, "Enr_" + str(j) + "_Estator")
        femm.hi_clearselected()

        femm.hi_selectarcsegment(5.7692 * math.cos((theta1 - 2) * degrau),
                                 5.7692 * math.sin((theta1 - 2) * degrau))  # Superior 4
        femm.hi_setarcsegmentprop(1, "Heat flux", 0, 4, "Enr_" + str(j) + "_Estator")
        femm.hi_clearselected()

        femm.hi_selectarcsegment(5 * math.cos((theta1 + 0.5) * degrau),
                                 5 * math.sin((theta1 + 0.5) * degrau))  # Inferior 1
        femm.hi_setarcsegmentprop(1, "Heat flux", 0, 5, "Enr_" + str(j) + "_Estator")
        femm.hi_clearselected()

        femm.hi_selectarcsegment(5 * math.cos((theta1 - 0.5) * degrau),
                                 5 * math.sin((theta1 - 0.5) * degrau))  # Inferior 2
        femm.hi_setarcsegmentprop(1, "Heat flux", 0, 6, "Enr_" + str(j) + "_Estator")
        femm.hi_clearselected()

        femm.hi_selectsegment(4.8 * math.cos((theta1 + 0.3) * degrau),
                              4.8 * math.sin((theta1 + 0.3) * degrau))  # Inferior 3
        femm.hi_setarcsegmentprop(1, "Heat flux", 0, 7, "Enr_" + str(j) + "_Estator")
        femm.hi_clearselected()

        femm.hi_selectsegment(5.3278 * math.cos((theta1 + 0.3) * degrau),
                              5.3278 * math.sin((theta1 + 0.3) * degrau))  # Lado 1
        femm.hi_setarcsegmentprop(1, "Heat flux", 0, 8, "Enr_" + str(j) + "_Estator")
        femm.hi_clearselected()

        femm.hi_selectsegment(5.3278 * math.cos((theta1 - 0.3) * degrau),
                              5.3278 * math.sin((theta1 - 0.3) * degrau))  # Lado 2
        femm.hi_setarcsegmentprop(1, "Heat flux", 0, 9, "Enr_" + str(j) + "_Estator")
        femm.hi_clearselected()

    #Aqui é onde não tem aquele código do Clear
    theta3 = 0
    for j in range(28):
        theta3 = 12.86 * j
        x3 = 3.6923 * math.cos(theta3 * degrau)

        y3 = 3.6923 * math.sin(theta3 * degrau)
        femm.hi_addconductorprop("Enr_" + str(j) + "_Rotor", 0, p_rotor[j], 0)

        femm.hi_selectarcsegment(3.6923 * math.cos((theta3 + 2) * degrau),
                                 3.6923 * math.sin((theta3 + 2) * degrau))  # arco superior 1
        femm.hi_setarcsegmentprop(1, "Heat flux1 ", 0, 11, "Enr_" + str(j) + "_Rotor")
        femm.hi_clearselected()

        femm.hi_selectarcsegment(3.6923 * math.cos((theta3 - 2) * degrau),
                                 3.6923 * math.sin((theta3 - 2) * degrau))  # arco superior 2
        femm.hi_setarcsegmentprop(1, "Heat flux1 ", 0, 12, "Enr_" + str(j) + "_Rotor")
        femm.hi_clearselected()

        femm.hi_selectsegment(4.5 * math.cos((theta3 + 0.2) * degrau),
                              4.5 * math.sin((theta3 + 0.2) * degrau))  # segmento superior 1
        femm.hi_setarcsegmentprop(1, "Heat flux1 ", 0, 13, "Enr_" + str(j) + "_Rotor")
        femm.hi_clearselected()

        femm.hi_selectsegment(4.5 * math.cos((theta3 - 0.2) * degrau),
                              4.5 * math.sin((theta3 - 0.2) * degrau))  # segmento superior 2
        femm.hi_setarcsegmentprop(1, "Heat flux1 ", 0, 14, "Enr_" + str(j) + "_Rotor")
        femm.hi_clearselected()

        femm.hi_selectsegment(3.6923 * math.cos((theta3 - 1) * degrau),
                              3.6923 * math.sin((theta3 - 1) * degrau))  # segmento lado 1
        femm.hi_setarcsegmentprop(1, "Heat flux1 ", 0, 15, "Enr_" + str(j) + "_Rotor")
        femm.hi_clearselected()

        femm.hi_selectsegment(3.6923 * math.cos((theta3 + 1) * degrau),
                              3.6923 * math.sin((theta3 + 1) * degrau))  # segmento lado 2
        femm.hi_setarcsegmentprop(1, "Heat flux1 ", 0, 16, "Enr_" + str(j) + "_Rotor")
        femm.hi_clearselected()

        femm.hi_selectarcsegment(2.93 * math.cos((theta3 + 0.2) * degrau),
                                 2.93 * math.sin((theta3 + 0.2) * degrau))  # arco inferior 1
        femm.hi_setarcsegmentprop(1, "Heat flux1 ", 0, 17, "Enr_" + str(j) + "_Rotor")
        femm.hi_clearselected()

        femm.hi_selectarcsegment(2.93 * math.cos((theta3 - 0.2) * degrau),
                                 2.93 * math.sin((theta3 - 0.2) * degrau))  # arco inferior 2
        femm.hi_setarcsegmentprop(1, "Heat flux1 ", 0, 18, "Enr_" + str(j) + "_Rotor")
        femm.hi_clearselected()
    p_rotor.clear()

    temp_sensor = 32
    femm.hi_addboundprop("Camisa", 2, 0, 0, 300, temp_sensor, 0)  # verificar esses 300
    for j in range(36):
        m = j * 10
        theta1 = t1 + m
        femm.hi_selectarcsegment(5.7692 * math.cos((theta1 + 2) * degrau),5.7692 * math.sin((theta1 + 2) * degrau))
        # temperatura externa
        femm.hi_setarcsegmentprop(1, "Camisa", 0, 10, "<None>")
        femm.hi_selectgroup(10)
        # femm.hi_setsegmentprop("", 0, 1, 1, "Camisa")
        femm.hi_setsegmentprop("Camisa", 0, 1, 0, 10, "<None>")#ja testei com 20, vamo com 10
        femm.hi_clearselected()
    femm.hi_clearselected()
    # Perdas no ferro do estator NOVO
    femm.hi_addconductorprop("Perdas_" + str(i - 1) + "_Estator", 0, pestator[i - 1], 0)
    femm.hi_selectarcsegment(5, 5.3)
    femm.hi_setarcsegmentprop(1, "<None>", 0, 40, "Perdas_" + str(i - 1) + "_Estator")
    femm.hi_clearselected()

    femm.hi_selectarcsegment(5, -5.3)
    femm.hi_setarcsegmentprop(1, "<None>", 0, 40, "Perdas_" + str(i - 1) + "_Estator")
    femm.hi_clearselected()

    femm.hi_selectarcsegment(-5, -5.3)
    femm.hi_setarcsegmentprop(1, "<None>", 0, 40, "Perdas_" + str(i - 1) + "_Estator")
    femm.hi_clearselected()

    femm.hi_selectarcsegment(-5, 5.3)
    femm.hi_setarcsegmentprop(1, "<None>", 0, 40, "Perdas_" + str(i - 1) + "_Estator")
    femm.hi_clearselected()

    femm.hi_addboundprop("Abiente", 2, 0, 0, 300, 25, 0)  # verificar esses 300 e 25 pq ta na temperatura ambiente
    femm.hi_selectarcsegment(0, 18.9)  # o q é
    femm.hi_setarcsegmentprop(1, "Ambiente", 0, 50, "<None>")  # parte de fora
    femm.hi_clearselected()
    # adicionar a tempera ambiente
    femm.hi_selectarcsegment(18.9, 0)
    femm.hi_setarcsegmentprop(1, "Ambiente", 0, 50, "<None>")  # parte de fora
    femm.hi_clearselected()

    # Salvar e Resolver
    femm.hi_createmesh()
    femm.hi_analyze(0)
    femm.hi_loadsolution()
    femm.hi_zoomnatural()
    # femm.ho_shownames()
    # femm.ho_hidenames()
    #femm.ho_showdensityplot(1, 0, 0, 323.2, 321.9)
    #femm.ho_hidedensityplot()

    femm.ho_savebitmap('T' + str(i) + '.bmp')
    femm.hi_saveas('Resultados/term_atual' + str(i) + '.feh')  # result termico

    # outrotest
    # femm.ho_savebitmap('Resultados/TERMICO.png')

    # pulo do gato, aqui ocorre o acoplamento
    # acho que ta errado
    md_testator = 0
    md_condestator = 0
    # Calculando condutividade dos enrolamentos do estator
    # a_cu = 0.0040
    # ro_cu = 1 / (58 * 1000000)
    a_cu = 0.0040
    ro_cu = 1 / (58)
    t1 = 5
    aux = 0
    cond_est.clear()
    t_estator.clear()
    for j in range(1, 37):
        m = (j - 1) * 10
        theta1 = t1 + m

        x1 = 5.3278 * math.cos(theta1 * degrau)
        y1 = 5.3278 * math.sin(theta1 * degrau)

        femm.ho_seteditmode('area')
        femm.ho_selectblock(x1, y1)
        aux3 = femm.ho_blockintegral(0)
        aux2 = aux3[0]
        print(f'{aux2}valor estator' + str(i))
        t_estator.append(aux2)
        femm.ho_clearblock()
        # aux = 1 / (1000000 * (ro_cu * (1 + a_cu * (aux2 - 300)))) #aqui deve ser o problema
        aux = ro_cu * (1 + a_cu * (aux2 - 293))  # Está em MS/m
        aux = 1 / aux
        print(f'{aux} valor aux' + str(i))
        cond_est.append(aux)

        md_testator = md_testator + aux2
        md_condestator = md_condestator + aux
        print(f'{md_testator}' + str(i))
        print(f'{md_condestator}' + str(i))

    md_testator = md_testator / 36
    md_condestator = md_condestator / 36
    print(f'{md_testator} estator temp')
    print(f'{md_condestator} estator cond')
    temperatura_enr_estator.append(md_testator)
    cond_enr_estator.append(md_condestator)
    print(cond_enr_estator)
    print(temperatura_enr_estator)

    # Calculando condutividade dos enrolamentos do rotor
    # a_al = 0.0040
    # ro_al = 1 / (34.45 * 1000000)
    a_al = 0.0040
    ro_al = 1 / (34.45)
    theta2 = 0
    md_trotor = 0
    t_rotor.clear()
    cond_rotor.clear()
    md_condrotor = 0
    for j in range(0, 27):
        theta2 = 12.86 * j

        x3 = 3.6923 * math.cos(theta2 * degrau)
        y3 = 3.6923 * math.sin(theta2 * degrau)

        femm.ho_seteditmode('area')
        femm.ho_selectblock(x3, y3)
        aux3 = femm.ho_blockintegral(0)
        aux2 = aux3[0]
        t_rotor.append(aux2)
        print(f'{aux2}valor rotor' + str(i))
        femm.ho_clearblock()
        # aux = 1 / (1000000 * (ro_al * (1 + a_al * (aux2 - 300))))
        aux = ro_al * (1 + a_al * (aux2 - 293))
        aux = 1 / aux
        print(f'{aux} valor aux' + str(i))
        cond_rotor.append(aux)

        md_condrotor = md_condrotor + aux
        md_trotor = md_trotor + aux2
        print(f'{md_condrotor}' + str(i))
        print(f'{md_trotor}' + str(i))

    temperatura_enr_rotor.append(md_trotor / 28)
    cond_enr_rotor.append(md_condrotor / 28)

    # femm.ho_close()
    # femm.hi_close()
    femm.closefemm()

    data = {'Rotor Temp': temperatura_enr_rotor, 'Stator Temp': temperatura_enr_estator,
            'Conductivity Rotor': cond_enr_rotor, 'Conductivity Stator': cond_enr_estator}

    df1 = pandas.DataFrame(data=data);
    df1.to_csv('Resultados/Resultados.csv')

    df2 = np.asarray(p_rotor);
    np.savetxt('Resultados/protor' + str(i) + '.csv', df2, delimiter=",")

    df3 = np.asarray(p_estator);
    np.savetxt('Resultados/p_estator' + str(i) + '.csv', df3, delimiter=",")

    df4 = np.asarray(cond_rotor);
    np.savetxt('Resultados/cond_rotor' + str(i) + '.csv', df4, delimiter=",")

    df5 = np.asarray(cond_est);
    np.savetxt('Resultados/cond_est' + str(i) + '.csv', df5, delimiter=",")

    df5 = np.asarray(torques);
    np.savetxt('Resultados/torque' + str(i) + '.csv', df5, delimiter=",")


    p_rotor.clear()
    p_estator.clear()

    # #Gráfico de condutividade deve ser feito com os vetores cond_enr_rotor e cond_enr_estator
    # plot(I, cond_enr_estator, cond_enr_rotor, 0)
    #
    # #Gráfico de perdas deve ser feito com os vetores media_enr_estator e media_enr_rotor
    # plot(I, media_enr_estator, media_enr_rotor, 1)
    #
    # #Gráfico de temperatura deve ser feito com os vetores temperatura_enr_rotor e temperatura_enr_estator
    # plot(I, temperatura_enr_estator, temperatura_enr_rotor, 2)

    i += 1
    id_final = ultimo_id()

    if (i > id_final):
        controle = False