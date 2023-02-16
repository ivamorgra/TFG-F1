import csv 
from csv import writer
from .models import Circuito, Piloto, Constructor
from pyspark import SparkContext
from pyspark.sql import SparkSession
from .bstracker import race_scrapping
from .meteo import get_weather
from pyspark.sql.functions import col

spark = SparkSession.Builder().appName("F1Analytics").getOrCreate()

def driver_basic_stats(driver_id):
    races = spark.read.csv("./datasets/results.csv", header=True,sep=",")
    races_driver = races.filter(races.driverId == driver_id)
    num_races = races_driver.count()
    num_wins = races.filter( (races.driverId == driver_id) & (races.position == 1)).count()
    sraces =  spark.read.csv("./datasets/sprint_results.csv", header=True,sep=",")
    num_sraces = sraces.filter(sraces.driverId == driver_id).count()
    num_swins = sraces.filter( (sraces.driverId == driver_id) & (sraces.position == 1)).count()
    
    stats = [num_races,num_wins,num_sraces,num_swins]
    return stats

def constructor_basic_stats(constructor_id):
    races = spark.read.csv("./datasets/constructor_standings.csv", header=True,sep=",")
    races_constructor = races.filter(races.constructorId == constructor_id)
    num_races = races_constructor.dropDuplicates(['raceId']).count()
    num_wins = races.filter( (races.constructorId == constructor_id) & (races.position == 1)).count()
    sraces =  spark.read.csv("./datasets/sprint_results.csv", header=True,sep=",")
    num_sraces = sraces.filter(sraces.constructorId == constructor_id).dropDuplicates(['raceId']).count()
    num_swins = sraces.filter( (sraces.constructorId == constructor_id) & (sraces.position == 1)).count()
    
    stats = [num_races,num_wins,num_sraces,num_swins]
    return stats

def process_race_data(races):
    res = []
    iterator = iter(races)
    while True:
        try:
            elemento = next(iterator)
            res.append((elemento[0],elemento[1],elemento[2]))
                
        except StopIteration:
            break
    return res

def get_circuit_bynameornacionality(input):
    res = []
    circuits = spark.read.csv("./datasets/circuits.csv", header=True,sep=",")
    circuits = circuits.filter( (circuits.name.contains(input)) | (circuits.country.contains(input)) ).collect()
    for c in circuits:
        circuit = Circuito.objects.get(pk=c.circuitId)
        res.append(circuit)
    return res

def get_constructor_bynameornacionality(input):
    res = []
    constr = spark.read.csv("./datasets/constructors.csv", header=True,sep=",")
    constructors = constr.filter( (constr.name.contains(input)) | (constr.nationality.contains(input)) ).collect()
    for c in constructors:
        con = Constructor.objects.get(pk=c.constructorId)
        res.append(con)
    return res

def get_driver_bynameornacionality(input):
    res = []
    drivers = spark.read.csv("./datasets/drivers.csv", header=True,sep=",")
    drivers = drivers.filter( (drivers.forename.contains(input)) | (drivers.surname.contains(input)) | (drivers.nationality.contains(input)) ).collect()

    for d in drivers:
        driver = Piloto.objects.get(pk=d.driverId)
        res.append(driver)
    return res

def get_races():
    #Obtener dataframe de carreras de la sesion de spark
    
    races = spark.read.csv("./datasets/races.csv", header=True,sep=",")
    #Pasar del dataframe de spark a un array de python
    races = races.select("raceId","name","year",).collect()
    #Conversion a iterador para pasarlo a la vista html
    res = process_race_data(races)
    res.sort(key=lambda x: x[2], reverse=True)
    return res

def get_race(race_id):
        
        races = spark.read.csv("./datasets/races.csv", header=True,sep=",")
        race = races.filter(races.raceId == race_id)
        res =  []
        year = int(race.collect()[0][1])
        name = race.collect()[0][4]
        #Obtención de datos de la carrera
        circuit,podium,pole = race_scrapping(race.collect()[0][7])
        date = race.collect()[0][5]
        time = race.collect()[0][6]
        ''' Procesamiento de la fecha para obtener el formato
         correcto para la API '''
        exists = check_notexists(name,year)
        if(exists[0]):
            start_date_param, end_date_param, end_time = process_meteo_date(date,str(year),time)
            if (len(circuit.split(","))> 2 ):
                location = circuit.split(",")[1]
            else:
                location = circuit.split(",")[-1]
        
            meteo = get_weather(location,start_date_param,end_date_param,time,end_time)
        
            #Actualización del registro
            with open('./datasets/meteo.csv','a',newline='') as f:
                w = writer(f)
                row = [(year,name,meteo[0][0],meteo[0][1],
                meteo[0][2],meteo[0][3],meteo[0][4])]  
                w.writerows(row)
                f.close()
                print ('Meteo Data Updated')
        else:
            meteo = exists[1]
        
        #Obtencón de datos específicos de la carrera del dataframe
        iterator = iter(race.collect())
        while True:
            try:
                elemento = next(iterator)
                res.append((elemento[0],elemento[1],elemento[2],elemento[3],elemento[4],elemento[5],elemento[6],elemento[7]))
            except StopIteration:
                break
        
        return res,circuit,podium,pole,meteo

def get_race_bynameorseason(input):

    races = spark.read.csv("./datasets/races.csv", header=True,sep=",")
    races = races.select("raceId","name","year",).filter( (races.name.contains(input)) | (races.year == input) ).collect()
    
    res = process_race_data(races)
    
    return res

def process_meteo_date(date,year,time):
    ''' la duracion de una carrera suele ser como máximo de 2 horas'''
    
    if (time != "\\N"):
        hours_time = int(time.split(":")[0]) + 2
        end_time = str(hours_time) + ":" + time.split(":")[1] + ":" + time.split(":")[2]
    else:
        ''' Como a priori no hay datos de la hora de inicio de la carrera,
        por defecto se le asigna la hora de inicio de la carrera a las 12:00:00'''
        time = "12:00:00"
        #La hora de finalizacion de la carrera se le asigna a las 14:00:00 por tanto
        end_time = "14:00:00"
    #El formato de fecha debe ser "2019-01-01T00:00:00"
    day = date.split("/")[0]
    month = date.split("/")[1]
    start_date_param = year + "-" + month + "-" + day + "T" + time
    end_date_param = year + "-" + month + "-" + day + "T" + end_time
    return start_date_param, end_date_param, end_time


''' Optimización de la API Meteo '''

def check_notexists(name,year):
    ''' Comprueba si la fecha de la carrera ya se encuentra en el dataset de meteo'''

    race = spark.read.csv("./datasets/meteo.csv", header=True,sep=",")
   
    race = race.select("temporada","nombre").filter((race.nombre.contains(name)) & (race.temporada == year)).collect()
    
    
    return ((len(race) == 0),race)

