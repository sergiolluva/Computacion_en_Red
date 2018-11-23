from flask import Flask, render_template, redirect, request
from beebotte import *
from pymongo import MongoClient
import re
import datetime
import requests
import numpy

base_datos = 'beebotte' #Base de datos usada para calcular la media de clics

#Datos de acceso a Beebotte
_hostname   = 'api.beebotte.com'
_token      = 'token_Rjjaqu0Qun4Mfi4k'
_channelname = "bbdd_beebotte"
bbt = BBT(token = _token, hostname = _hostname)

#Base de datos MongoDB
mongoClient = MongoClient('localhost', 27017)
db = mongoClient.noticias_v1
collection = db.meneame

app = Flask(__name__)

@app.route("/", methods=["GET"])
def inicio():
    datos=bbt.read('bbdd_beebotte', 'clics', limit=1) #[]
    fila = datos[0] #{}
    clics = fila.get("data") #data=clics
    
    datos=bbt.read('bbdd_beebotte', 'meneos', limit=1)
    fila = datos[0]
    meneos = fila.get("data")

    datos=bbt.read('bbdd_beebotte', 'titulo', limit=1)
    fila = datos[0]
    titulo = fila.get("data")  

    datos=bbt.read('bbdd_beebotte', 'date', limit=1)
    fila = datos[0]
    date = fila.get("data")

    return render_template("index.html", titulo=titulo, clics=clics, meneos=meneos, date=date)

@app.route("/valor_medio")
def valor_medio():
	global base_datos
	numero_clics=collection.count()
	
	if base_datos=='beebotte':
		datos = bbt.read('bbdd_beebotte', 'clics', limit=numero_clics)
		array_datos = []
		for i in datos:
			array_datos.append(i['data'])
		media_clics = numpy.mean(array_datos)
		media_clics="{0:.2f}".format(media_clics)
		base_datos='mongo'
	else:
		datos = collection.find().limit(numero_clics)
		array_datos = []
		for i in datos:
			array_datos.append(int(i['clics']))
		media_clics = numpy.mean(array_datos)
		media_clics="{0:.2f}".format(media_clics)
		base_datos='beebotte'

	#La base de datos es la opuesta
	return render_template("valor_medio.html", media_clics = media_clics, base_datos=base_datos)

@app.route("/umbral_clics", methods=["POST"])
def umbral_clics():
	umbral = request.form["umbral_clics"]
	
	datos = collection.find({}, {'_id':False})
	datos_umbral = []
	#Primer dato de resultado es el mas antiguo
	for fila in datos:
		if int(fila.get("clics")) > int(umbral):
			datos_umbral .append(fila)

	datos_umbral  = datos_umbral [(len(datos_umbral )-10):len(datos_umbral )]
	datos_umbral = datos_umbral [::-1] #Ordenar, el primero más reciente
	return render_template("umbral_clics.html", datos_umbral=datos_umbral)

@app.route("/umbral_meneos", methods=["POST"])
def umbral_meneos():
	umbral = request.form["umbral_meneos"]
	
	datos = collection.find({}, {'_id':False})
	datos_umbral = []
	#Primer dato de resultado es el mas antiguo
	for fila in datos:
		if int(fila.get("meneos")) > int(umbral):
			datos_umbral .append(fila)

	datos_umbral  = datos_umbral [(len(datos_umbral )-10):len(datos_umbral )]
	datos_umbral = datos_umbral [::-1] #Ordenar, el primero más reciente
	return render_template("umbral_meneos.html", datos_umbral=datos_umbral)

@app.route("/grafica_clics")
def grafica_clics():
    return render_template("grafica_clics.html")

@app.route("/grafica_meneos")
def grafica_meneos():
    return render_template("grafica_meneos.html")

if __name__ == '__main__':
  app.run(host='0.0.0.0', debug=True)
