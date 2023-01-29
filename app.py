from flask import Flask, request, send_file, render_template, jsonify
import os
from app_service import pegar_data_formatada, pegar_hora_formatada, escrever_dados_arquivo_csv, registrar_dado_no_bd, \
   pegar_dados_do_sensor, pegar_todos_dados_bd, pegar_ultimo_dado_do_sensor

app = Flask(__name__) #nome

#primeira rota
@app.route('/')
def home(): #def = função
   return render_template("home.html")

#segunda rota
@app.route('/dados',methods = ['POST']) #dizer o metodo da rota, nesse caso é post
def receber(): #o tipo da função
   dado = request.json#requisitando um arquivo json
   dado_armazenar = {"medicao": dado["medicao"]}#dicionario ou objeto
   print(dado)
   dado_armazenar["data"] = pegar_data_formatada()
   dado_armazenar["hora"] = pegar_hora_formatada()
   print(dado_armazenar)
   registrar_dado_no_bd(dado_armazenar, dado["sensor"])
   return "deu tudo certo"

#terceira rota de baixar os dados em formato de excel
@app.route("/baixar_dado")
def baixar_dado ():
   escrever_dados_arquivo_csv(pegar_todos_dados_bd())
   path = os.getcwd()+"/output.zip" #caminho do codigo atual
   return send_file(path, as_attachment=True) #send_file do flask pegue o arquivo do direotiro pra poder baixar

@app.route("/visualizar_dado")
def visualizar_dado ():
   return jsonify(pegar_todos_dados_bd())

@app.route("/ultimo-dado-sensor/<sensor>")
def ultimo_dado_sensor (sensor):
   return jsonify(pegar_ultimo_dado_do_sensor(sensor))

#cors = CORS(app, resource={r"/*": {"origins": "*"}})

def main():
    app.run(host="0.0.0.0", port=5000)

if __name__ == "__main__":
    main()

