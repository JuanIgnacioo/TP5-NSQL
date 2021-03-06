from flask import Flask
from pymongo import MongoClient
from flask import jsonify, request, redirect, url_for
from flask_cors import CORS
from conexion_api import get_data
from conexionesDB import inicializar_base1,inicializar_base2
import json

from hasheo import hasheo_base, hashear


app = Flask(__name__)
CORS(app)

#Funcion para inicializar bases
def inicializar_bases():    
    db = inicializar_base1()
    db.cryp.drop()#borramos si contenia alguna info
    data = get_data()
    #print(data)
    db.cryp.insert_many(data) # inserto los datos en la bd1
    data = db.cryp.find({},{"_id":0})#obtener datos de la bd1       
    hash_data = hasheo_base(data) #hashear la data para meterla en la bdd aux
    #print(hash_data)
    db2 = inicializar_base2()
    db2.cryp.drop()
    db2.cryp.insert_many(hash_data)#metemos la data hasheada en la bdd2
    print('ok')
 
 #inicializamos cuando arranca la app

inicializar_bases()

def validacionDos (item,db2): # validacion para buscar x  id
    aux = False
    data1 = hashear(item) #hasheo la data y la busco en la bdd hasheada para ver si coincide
    data2 = db2.cryp.find_one({"cmc_rank":item["cmc_rank"]}, {"_id":0}) #buscar en base al ranking
    if (data1 == data2["hash"]):
        aux = True
    else: 
        aux = False
    
    return aux

@app.route('/obtenerSegunId', methods =['POST']) #obtener una criptomoneda segun el id
def obtenerSegunId():
    try:
        if request.method == 'POST':
            id = request.json['id']
            #print(id)
            db = inicializar_base1()
            db2 = inicializar_base2()
            aux = db.cryp.find_one({"id": str(id)}, {"_id": 0})
            #print(res)
            if (aux != None) and (validacionDos(aux,db2) == False):
                raise Exception ('error info')
            return jsonify(aux)
    except (Exception) as err:
        return str(err), 500



@app.route('/borrarCrypto', methods=['POST'])
def borrarCrypto():
    try:        
        if request.method == 'POST':
            rank = request.json['rank']
            db = inicializar_base1()
            db2 = inicializar_base2()
            db.cryp.delete_one({"cmc_rank":str(rank)})
            db2.cryp.delete_one({"cmc_rank":str(rank)})
            return "deleted"
    except (Exception) as err:
        return str(err), 500
   
#---------------------------------------------
def validacion (db1_cryp,db2): #validacion para cuando quiero obtener todas las cryptomonedas, #top 5 y top20                       
    aux = False
    for i in db1_cryp:
        data1 = hashear(i)
        data2 = db2.cryp.find_one({"cmc_rank": i["cmc_rank"]}, {"_id": 0})
        if (data1 == data2["hash"]): # verifico si el resultado de la bdd 1 es igual a la hasheada
            aux = True
        else:
            aux = False
            
    return aux

@app.route('/listarTodasCrypto', methods=['GET']) #funciona
def listarTodasCrypto():
    if request.method == 'GET':
        db = inicializar_base1()
        db2 = inicializar_base2()
        aux = []
        for x in db.cryp.find({}, {"_id": 0}):
            aux.append(x)
        if (validacion(aux,db2) == False) or (db.cryp.count() != db2.cryp.count()):
            print('informacion erronea')
        return jsonify(aux)


@app.route('/top5', methods=['GET']) #funciona
def top5():
    if request.method == 'GET':
        db = inicializar_base1()
        db2 = inicializar_base2()
        aux = []
        for x in db.cryp.find({"$where": "parseInt(this.cmc_rank) <=5"}, {"_id": 0}):
            aux.append(x)
            #print(aux)
        if (validacion(aux,db2) == False) or (db.cryp.count() != db2.cryp.count()):
            print('informacion erronea')
        return jsonify(aux)

@app.route('/top20', methods=['GET']) # funciona
def top20():
    if request.method == 'GET':
        db = inicializar_base1()
        db2 = inicializar_base2()
        aux = []
        for x in db.cryp.find({"$where": "parseInt(this.cmc_rank) <=20"}, {"_id": 0}):
            aux.append(x)
            #print(aux)
        if (validacion(aux,db2) == False) or (db.cryp.count() != db2.cryp.count()):
            print('informacion erronea')
        return jsonify(aux)



if __name__ == '__main__':
    app.run(host='backend', port ='5000', debug=True)