import csv 
from csv import writer
from .models import Circuito, Piloto, Constructor
from pyspark import SparkContext
from pyspark.sql import SparkSession
from .bstracker import race_scrapping
from .meteo import get_weather
from .spark_queries import get_data_race,check_notexists,process_meteo_date


spark = SparkSession.Builder().appName("F1Analytics").getOrCreate()



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