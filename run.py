# -*- coding: utf-8 -*-
from pymongo import MongoClient
from beebotte import *
from datetime import datetime
import urllib.request as urlreq
import re
import sys
import unicodedata
import numpy

#Datos de acceso a beebotte
_hostname   = 'api.beebotte.com'
_token      = 'token_Rjjaqu0Qun4Mfi4k'
_channelname = "bbdd_beebotte"
bbt = BBT(token = _token, hostname = _hostname)

class meneame:

    def __init__(self, titulo, clics, meneos, date):
        self.titulo = titulo
        self.clics = clics
        self.meneos = meneos
        self.date = date

    def toDBCollection (self):
        return {
            "titulo":self.titulo,
            "clics":self.clics,
            "meneos": self.meneos,
            "date":self.date
        }

    def __str__(self):
        return "titulo: %s - clics: %i - meneos: %i - date: %s" \
               %(self.titulo, self.clics, self.meneos, self.date)

#Fecha y hora
today=datetime.now()
today=today.strftime("%X, %x")

url = "https://www.meneame.net"
req = urlreq.Request(url)
htmlfile = urlreq.urlopen(req).read()
texto_html = htmlfile.decode(encoding='UTF-8')

#Extraer titulo con expresiones regulares
titulo = re.findall('<h2>(.*?)</h2>',texto_html)
titulo = str(re.findall('>(.*?)</a>',titulo[0]))
titulo=titulo[3:len(titulo)-2]

#Extraer meneos con expresiones regulares
meneos = re.findall('<a id="a-votes-.*?>(\d*)<\/a>',texto_html)
meneos = int(meneos[0])

#Extraer clics con expresiones regulares
clics = re.findall('<div\s*class="clics">\s*(\d*)\sclics\s*<\/div>',texto_html)
clics = int(clics[0])

datos = [
    meneame(titulo,clics,meneos,today)
]

#Conexión a MongoDB
mongoClient = MongoClient('localhost', 27017)
#Conexión a la base de datos
db = mongoClient.noticias_v1
#Obtenemos una coleccion
collection = db.meneame
#Insertar los datos en MongoDB
for meneame in datos:
    collection.insert(meneame.toDBCollection())

#Escritura masiva en Beebotte
bbt.writeBulk(_channelname, [
    {"resource": "titulo", "data": titulo},
    {"resource": "clics", "data": clics},
    {"resource": "meneos", "data": meneos},
    {"resource": "date", "data": today}
])

mongoClient.close()
