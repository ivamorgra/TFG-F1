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

def get_driver_byid(id):
    return Piloto.objects.get(pk=id)

def get_constructor_byid(id):
    return Constructor.objects.get(pk=id)

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
        race_collector = race.collect()
        circuit_id = int(race_collector[0][3])
        circuit = Circuito.objects.get(pk=circuit_id)
        
        year = int(race_collector[0][1])
        
        name = race_collector[0][4]
        #Obtención de datos de la carrera
        podium,pole = race_scrapping(race_collector[0][7])
        data_stats = get_data_race(race_id)

        #Datos sobre la vuelta rápida y la máxima velocidad alcanzada
        data_fl = data_stats[0]
        data_ms = data_stats[1]

        date = race_collector[0][5]
        time = race_collector[0][6]
        ''' Procesamiento de la fecha para obtener el formato
         correcto para la API '''

        if (year >= 2000):
            exists = check_notexists(name,year)
            if(exists[0]):
                start_date_param, end_date_param, end_time = process_meteo_date(date,str(year),time)
            
                meteo = get_weather(circuit.localizacion,start_date_param,end_date_param,time,end_time)
            
                #Actualización del registro
                with open('./datasets/meteo.csv','a',newline='') as f:
                    w = writer(f)
                    row = [(year,name,meteo[0][0],meteo[0][1],
                    meteo[0][2],meteo[0][3],meteo[0][4])]  
                    w.writerows(row)
                    f.close()
                    print ('Meteo Data Updated')
            else:
                data = spark.read.csv("./datasets/meteo.csv", header=True,sep=",")
                data = data.filter( (data.temporada == year) & (data.nombre == name) ).collect()[0]
                meteo = []
                meteo.append((data.min_temp,data.temperatura,data.precipitacion
                ,data.humedad,data.condiciones))
                

        else:
            
            meteo = []
            meteo.append("No hay datos disponibles ya que la carrera se disputó antes del año 2000")
        #Obtencón de datos específicos de la carrera del dataframe
        iterator = iter(race.collect())
        while True:
            try:
                elemento = next(iterator)
                res.append((elemento[0],elemento[1],elemento[2],elemento[3],elemento[4],elemento[5],elemento[6],elemento[7]))
            except StopIteration:
                break
        
        return res,circuit,podium,pole,meteo,data_fl,data_ms

def get_data_race(race_id):
    NO_DATA = "No hay datos disponibles"
    res = []
    ''' Obtenemos la vuelta más rápida, máx velocidad a la que se llegó'''

    results = spark.read.csv("./datasets/results.csv", header=True,sep=",")

    #Obtenemos los campos que nos interesan de la carrera seleccionada
    df = results.select("raceId","driverId","constructorId",
    "position","fastestLap","fastestLapTime","fastestLapSpeed").filter(results.raceId == race_id)
    
    collector = df.collect()
    if (len(collector) == 0):
        res.append((NO_DATA,NO_DATA,NO_DATA,NO_DATA))
        res.append((NO_DATA,NO_DATA,NO_DATA,NO_DATA))
        return res
    else:

        fl_data = df.orderBy(df.fastestLapTime).collect()[0]

        if (fl_data[2] == "\\N" or fl_data[3] == "\\N" or fl_data[-2] == "\\N"):
            res.append((NO_DATA,NO_DATA,NO_DATA,NO_DATA))
        else:
        #Obtenemos el nombre del piloto
            flobj_driver = get_driver_byid(fl_data[1])
            fl_driver = flobj_driver.nombre + " " + flobj_driver.apellidos

            #Obtenemos el nombre del constructor
            fl_constructor = get_constructor_byid(fl_data[2]).nombre

            res.append((flobj_driver.id,fl_driver,fl_constructor,fl_data[-2]))

        #Obtenemos la máxima velocidad
        max_speed = df.orderBy(df.fastestLapSpeed).collect()[0]

        if (max_speed[2] == "\\N" or max_speed[3] == "\\N" or max_speed[-1] == "\\N"):
            res.append((NO_DATA,NO_DATA,NO_DATA,NO_DATA))
        else:
            #Obtenemos el nombre del piloto
            driver = get_driver_byid(max_speed[1])
            ms_driver = driver.nombre + " " + driver.apellidos

            #Obtenemos el nombre del constructor
            ms_constructor = get_constructor_byid(max_speed[2]).nombre
            res.append((driver.id,ms_driver,ms_constructor,max_speed[-1]))

    return res


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

