import csv 
from .models import Circuito, Piloto, Constructor
from pyspark import SparkContext
from pyspark.sql import SparkSession

spark = SparkSession.Builder().appName("F1Analytics").getOrCreate()


def populate():
    c=load_circuits()
    p = load_drivers()
    co = load_constructors()
    
    '''
    g=populateGenres()
    (u, us)=populateUsers()
    (m, mo)=populateMovies()
    p=populateRatings(u,m)  #USAMOS LOS DICCIONARIOS DE USUARIOS Y PELICULAS PARA ACELERAR LA CARGA EN PUNTUACIONES
    return (o,g,us,mo,p)
    '''
    return (c,p,co)

def load_circuits():
    ''' Borrado de los datos de la tabla por si ya estaban cargados de antes'''
    Circuito.objects.all().delete()

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

def load_drivers():
    Piloto.objects.all().delete()

    '''Creación de lista de objetos de tipo Piloto'''
    drivers = []
    '''Carga de los datos de los circuitos'''
    df = spark.read.csv("./datasets/drivers.csv", header=True,sep=",")
    for row in df.collect():

        driver = Piloto(
            id = row[0],
            nombre = row[4],
            apellidos = row[5],
            fecha_nacimiento = row[6],
            nacionalidad = row[7],
            abreviatura = row[3],
            enlace = row[8],
        )
        drivers.append(driver)
    
    Piloto.objects.bulk_create(drivers)
    return Piloto.objects.count()

def load_constructors():
    Constructor.objects.all().delete()

    '''Creación de lista de objetos de tipo Piloto'''
    constructors = []
    '''Carga de los datos de los circuitos'''
    df = spark.read.csv("./datasets/constructors.csv", header=True,sep=",")
    for row in df.collect():

        constructor = Constructor(
            id = row[0],
            referencia = row[1],
            nombre = row[2],
            nacionalidad = row[3],
            enlace = row[4],
        )
        constructors.append(constructor)
    
    Constructor.objects.bulk_create(constructors)
    return Constructor.objects.count()

def load_df():
    cons_res = spark.read.csv("./datasets/constructor_results.csv", header=True,sep=",")
    races = spark.read.csv("./datasets/races.csv", header=True,sep=",")
    seasons =  spark.read.csv("./datasets/seasons.csv", header=True,sep=",")
    results = spark.read.csv("./datasets/results.csv", header=True,sep=",")
    sresults = spark.read.csv("./datasets/sprint_results.csv", header=True,sep=",")
    status =  spark.read.csv("./datasets/status.csv", header=True,sep=",")
    const_clas = spark.read.csv("./datasets/constructor_standings.csv", header=True,sep=",")
    laps =  spark.read.csv("./datasets/lap_times.csv", header=True,sep=",")
    stops =  spark.read.csv("./datasets/pit_stops.csv", header=True,sep=",")
    qualy_results =  spark.read.csv("./datasets/qualifying.csv", header=True,sep=",")

    return cons_res.count(),races.count(),seasons.count(),results.count(),sresults.count(),status.count(),const_clas.count(),laps.count(),stops.count(),qualy_results.count()