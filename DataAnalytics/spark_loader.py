import csv 
from .models import Circuito
from pyspark import SparkContext
from pyspark.sql import SparkSession

spark = SparkSession.Builder().appName("F1Analytics").getOrCreate()


def populate():
    o=load_circuits()
    '''
    g=populateGenres()
    (u, us)=populateUsers()
    (m, mo)=populateMovies()
    p=populateRatings(u,m)  #USAMOS LOS DICCIONARIOS DE USUARIOS Y PELICULAS PARA ACELERAR LA CARGA EN PUNTUACIONES
    return (o,g,us,mo,p)
    '''
    return o

def load_circuits():
    '''Creación de lista de objetos de tipo Circuito'''
    circuits = []
    '''Carga de los datos de los circuitos'''
    df = spark.read.csv("./datasets/circuits.csv", header=True,sep=",")
    for row in df.collect():

        if row[7] == '\\N':
            circuit = Circuito(
            id = row[0],
            nombre_referencia = row[1],
            nombre = row[2],
            localizacion = row[3],
            pais = row[4],
            latitud = row[5],
            longitud = row[6],
            altura = None,
            enlace = row[8]
            )
        else:

            circuit = Circuito(
                id = row[0],
                nombre_referencia = row[1],
                nombre = row[2],
                localizacion = row[3],
                pais = row[4],
                latitud = row[5],
                longitud = row[6],
                altura = row[7],
                enlace = row[8]
            )
            
        circuits.append(circuit)
    
    Circuito.objects.bulk_create(circuits)
    return Circuito.objects.count()