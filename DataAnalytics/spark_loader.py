import csv 
from .models import Circuito, Piloto, Constructor, Carrera, Periodo
from pyspark import SparkContext
from pyspark.sql import SparkSession
import datetime
from .spark_queries import is_active_driver
from .bstracker import drivers_scrapping,constructors_scrapping,get_actual_team_byname
from pyspark.sql.functions import col


spark = SparkSession.Builder().appName("F1Analytics").getOrCreate()

URL = 'https://www.formula1.com/'

def populate():
    c=load_circuits()
    co = load_constructors()
    p = load_drivers()
    pe = load_periods()
    r = load_races()
    print ("Número de periodos cargados: ")
    print (pe)
    return (c,p,co,r)



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
    actual_drivers = drivers_scrapping()
    
    '''Creación de lista de objetos de tipo Piloto'''
    drivers = []
    '''Carga de los datos de los circuitos'''
    df = spark.read.csv("./datasets/drivers.csv", header=True,sep=",")
    for row in df.collect():
        is_active = is_active_driver(actual_drivers,row.forename,row.surname)
        
        driver = Piloto(
            id = row[0],
            nombre = row[4],
            apellidos = row[5],
            fecha_nacimiento = row[6],
            nacionalidad = row[7],
            abreviatura = row[3],
            enlace = row[8],
            activo = is_active
        )
        drivers.append(driver)
    
    Piloto.objects.bulk_create(drivers)
    return Piloto.objects.count()

def load_constructors():
    Constructor.objects.all().delete()
    actual_teams = constructors_scrapping()
    '''Creación de lista de objetos de tipo Piloto'''
    constructors = []
    '''Carga de los datos de los circuitos'''
    df = spark.read.csv("./datasets/constructors.csv", header=True,sep=",")
    for row in df.collect():
        nombre = row.name
        is_active = True
        if (len(list(filter(lambda x: nombre in x, actual_teams))) == 0):
            is_active = False
        constructor = Constructor(
            id = row[0],
            referencia = row[1],
            nombre = row[2],
            nacionalidad = row[3],
            enlace = row[4],
            activo = is_active
        )
        constructors.append(constructor)
    
    Constructor.objects.bulk_create(constructors)
    return Constructor.objects.count()


def load_races():
    ''' Borrado de los datos de la tabla por si ya estaban cargados de antes'''
    Carrera.objects.all().delete()

    '''Creación de lista de objetos de tipo Carrera'''
    races = []
    '''Carga de los datos de los carreras'''
    df = spark.read.csv("./datasets/races.csv", header=True,sep=",")
    for row in df.collect():
        
        if (int(row[1]) > 2020 ):
            fecha = row[5].split("/")
            date_time_str = row[1] + "-" + fecha[1] + "-" + fecha[0] + ' ' + row[6]
            date_time_obj = datetime.datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')
            race = Carrera(
                id = row[0],
                temporada = row[1],
                numero = row[2],
                nombre = row[4],
                fecha = date_time_obj,
                enlace = row[-1],
                circuito = Circuito.objects.get(id = row[3])
            )
            races.append(race)
    
    Carrera.objects.bulk_create(races)
    return Carrera.objects.count()


def load_periods():
    Periodo.objects.all().delete()
    fecha_actual = datetime.datetime.now()
    temporada_actual = int(fecha_actual.year)
    pilotos = Piloto.objects.all()
    teams = spark.read.csv("./datasets/constructors.csv", header=True,sep=",")
    periods = []
    for piloto in pilotos:
        
        if (piloto.activo == True):
            list_actual_team_name = []
            ''' Si el piloto está activo, añadimos el periodo actual'''
            actual_team_name = get_actual_team_byname(piloto.apellidos)
                
            if (actual_team_name == "Red Bull Racing"):
                actual_team_name = "Red Bull"
            elif (actual_team_name == "Alpine"):
                actual_team_name = "Alpine F1 Team"

            list_actual_team_name.append(actual_team_name)
            print (list_actual_team_name)
            query_name = teams.filter( (teams.name.isin(list_actual_team_name)) | teams.constructorRef.isin(list_actual_team_name) )
            print (query_name)
            print (query_name.collect()[0])
            period = Periodo(
                temporada_inicio = temporada_actual,
                temporada_fin = temporada_actual,
                constructor = Constructor.objects.get(nombre = query_name.collect()[0].name),
                piloto = piloto
            )
            
            periods.append(period) 
        
    Periodo.objects.bulk_create(periods)
    return Periodo.objects.count()

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