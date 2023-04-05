import csv 
from csv import writer
from .models import Circuito, Piloto, Constructor
from pyspark import SparkContext
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum,avg, weekofyear
from pyspark.sql.types import DateType
from django.db.models import Q
import datetime
from .models import Carrera

spark = SparkSession.Builder().appName("F1Analytics").getOrCreate()

''' Diccionario clave -> abreviatura, valor -> nombre de usuario en twitter'''
TWITTER_PROFILE = {'HAM': 'LewisHamilton', 'ALO':'alo_oficial','BOT':'ValtteriBottas',
                   'MAG':'KevinMagnussen','VER':'Max33Verstappen','SAI':'Carlossainz55','OCO':'OconEsteban',
                   'STR':'lance_stroll','GAS':'PierreGASLY','LEC':'Charles_Leclerc','NOR':'LandoNorris','RUS':'GeorgeRussell63',
                   'ALB':'alex_albon','TSU':'yukitsunoda07','PER':'SChecoPerez','ZHO':'ZhouGuanyu24','PIA':'OscarPiastri',
                   'HUL':'HulkHulkenberg','DE ':'nyckdevries','SAR':'LoganSargeant'}

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

def get_country_races_by_driver(driver_id):
    
    results= spark.read.csv("./datasets/results.csv", header=True,sep=",")
    races = spark.read.csv("./datasets/races.csv", header=True,sep=",")
    
    results = results.join(races, on=["raceId"], how="inner").filter(col("year") >= 2021)
    counts = results.select('raceId').collect()
    
    ids = []
    for c in counts:
        ids.append(int(c.raceId))
    
    
    paises = {}

    for id in ids:
        key = "\"" + Carrera.objects.get(pk=id).circuito.pais + "\""
        key.replace("'","")
        
        if key in paises:
            paises[key] += 1
        else:
            paises[key] = 1
    
    return list(paises.keys()), list(paises.values())
    
    
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


#region Obtener piloto activo por nombre

def get_active_driver_byname(name):

    try :
        driver = Piloto.objects.get(Q(apellidos=name),activo=1)
    
    except Piloto.DoesNotExist:
        driver = None

    return driver
#endregion

def get_driver_byid(id):
    return Piloto.objects.get(pk=id)

def get_constructor_byid(id):
    return Constructor.objects.get(pk=id)

''' Devuelve True si el piloto está activo en la temporada actual'''
def is_active_driver(actual_drivers,name,surname):
    
    for driver in actual_drivers:
        if (driver[0] == name and driver[1] == surname):
            return True
    return False

def get_races():
    #Obtener dataframe de carreras de la sesion de spark
    
    races = spark.read.csv("./datasets/races.csv", header=True,sep=",")
    #Pasar del dataframe de spark a un array de python
    races = races.select("raceId","name","year",).collect()
    #Conversion a iterador para pasarlo a la vista html
    res = process_race_data(races)
    res.sort(key=lambda x: x[2], reverse=True)
    return res



''' Devuelve la evolución de puntos
    en las carreras de los 3 primeros pilotos actuales'''

#region Evolución Top 3 Pilotos (vale para la comparativa entre 2 pilotos)
def get_top3drivers_evolution(abreviaturas):
    ''' LOS PARÁMETROS SON:
    - Abreviaturas de los 3 pilotos (o 2)
    RETURN: Carreras de la temporada, listas de puntos de los 3 pilotos'''
    
    puntuation_driver1 = []
    puntuation_driver2 = []
    puntuation_driver3 = []

    #Obtenemos la fecha actual
    actual_date = datetime.datetime.now()
    #Obtenemos el año actual
    actual_year = actual_date.year

    #Obtenemos las carreras hasta la fecha
    races = Carrera.objects.filter(temporada=actual_year)
    #Pasamos las carreras a un array de python
    races_list = races.values_list('id')
    names_races_list = races.values_list('nombre')
    #Obtenemos los pilotos 
    
    try:
        piloto_1 = Piloto.objects.get(abreviatura=abreviaturas[0],activo=1)
        piloto_2 = Piloto.objects.get(abreviatura=abreviaturas[1],activo=1)
        piloto_3 = Piloto.objects.get(abreviatura=abreviaturas[2],activo=1)

    except Exception as e:
        print(e)
    
    #Obtenemos los puntos de los pilotos en cada carrera

    results = spark.read.csv("./datasets/results.csv", header=True,sep=",")
    for r in races_list:
        data_driver1 = results.filter( (results.raceId == r[0]) & (results.driverId == piloto_1.id) ).collect()
        data_driver2 = results.filter( (results.raceId == r[0]) & (results.driverId == piloto_2.id) ).collect()
        data_driver3 = results.filter( (results.raceId == r[0]) & (results.driverId == piloto_3.id) ).collect()
        
        if (len(data_driver1) > 0):
            puntuation_driver1.append(data_driver1[0].points)
        else:
            puntuation_driver1.append(0)
        if (len(data_driver2) > 0):
            puntuation_driver2.append(data_driver2[0].points)
        else:
            puntuation_driver2.append(0)
        if (len(data_driver3) > 0):
            puntuation_driver3.append(data_driver3[0].points)
        else:
            puntuation_driver3.append(0)
    

    return list(races_list),list(names_races_list),puntuation_driver1,puntuation_driver2,puntuation_driver3
#endregion

#region Evolución Top 3 Constructores


''' Función que devuelve la evolución de puntos de 
    los 3 primeros constructores actuales
    PARAMS: Abreviaturas de los 3 constructores'''

def get_top3teams_evolution(names):
    ''' LOS PARÁMETROS SON:
    - Carreras de la temporada
    - Nombre de los 3 constructores
    RETURN: Carreras de la temporada, listas de puntos de los 3 pilotos'''
    
    puntuation_team1 = []
    puntuation_team2 = []
    puntuation_team3 = []

    actual_year = datetime.datetime.now().year

    #Obtenemos las carreras 
    races = Carrera.objects.filter(temporada=actual_year)
    races_list = races.values_list('id')

    try:
        
        team_1 = Constructor.objects.filter(Q(nombre__icontains= names[0].split(' ')[0] ), activo = 1).get()
        
        team_2 = Constructor.objects.filter(Q(nombre__icontains= names[1].split(' ')[0] ), activo = 1).get()
        team_3 = Constructor.objects.filter(Q(nombre__icontains= names[2].split(' ')[0] ), activo = 1).get()

        #Obtenemos los puntos de los equipos en cada carrera
        results = spark.read.csv("./datasets/constructor_results.csv", header=True,sep=",")
        
        for r in races_list:
            
            data_team1 = results.filter( (results.raceId == r[0]) & (results.constructorId == team_1.id) ).collect()
            
            
            data_team2 = results.filter( (results.raceId == r[0]) & (results.constructorId == team_2.id) ).collect()
            
            data_team3 = results.filter( (results.raceId == r[0]) & (results.constructorId == team_3.id) ).collect()

            if (len(data_team1) > 0):
                puntuation_team1.append(data_team1[0].points)
            else:
                puntuation_team1.append(0)
            if (len(data_team2) > 0):
                puntuation_team2.append(data_team2[0].points)
            else:
                puntuation_team2.append(0)
            if (len(data_team3) > 0):
                puntuation_team3.append(data_team3[0].points)
            else:
                puntuation_team3.append(0)
    
    except Exception as e:
        print(e)
        

    return puntuation_team1,puntuation_team2,puntuation_team3

#endregion


#region Progreso de temporada

def get_season_progress():

    ''' Vemos cuantas carreras hay en la temporada
        y cuantas han pasado'''
    num_season_races = Carrera.objects.filter(temporada=datetime.datetime.now().year).count()
    num_past_races = Carrera.objects.filter(temporada=datetime.datetime.now().year).filter(fecha__lt=datetime.datetime.now()).count()

    return num_past_races/num_season_races

#endregion

#region Comparativa de pilotos

def get_pilots_comparison(names):
    ''' Abreviaturas debe ser una lista de 2 abreviaturas
    correspondiente a dos pilotos'''
    driver_1 = get_active_driver_byname(names[0])
    driver_2 = get_active_driver_byname(names[1])

    id_driver1 = driver_1.id
    id_driver2 = driver_2.id

    #Obtenemos los datos estadísticos de los pilotos
    
    wins_1 = get_num_wins_season_pilot(id_driver1)
    wins_2 = get_num_wins_season_pilot(id_driver2)

    #Obtenemos el pipeline de la temporada
    ids = [id_driver1,id_driver2]
    races_list,names_races_list,puntuation_driver1,puntuation_driver2 = get_comparation_drivers_evolution(ids)

    res = {
        'wins_1': wins_1,
        'wins_2': wins_2,
        'races_list':races_list,
        'names_races_list': names_races_list,
        'puntuation_driver1': puntuation_driver1,
        'puntuation_driver2': puntuation_driver2
    }

    return res
#endregion


#region Evolución 2 pilotos
def get_comparation_drivers_evolution(ids):
    ''' LOS PARÁMETROS SON:
    - Ids de los 2 pilotos
    RETURN: Carreras de la temporada, listas de puntos de los 2 pilotos'''
    
    puntuation_driver1 = []
    puntuation_driver2 = []

    #Obtenemos la fecha actual
    actual_date = datetime.datetime.now()
    #Obtenemos el año actual
    actual_year = actual_date.year

    #Obtenemos las carreras hasta la fecha
    races = Carrera.objects.filter(temporada=actual_year)
    #Pasamos las carreras a un array de python
    races_list = races.values_list('id')
    names_races_list = races.values_list('nombre')
    
    
    #Obtenemos los puntos de los pilotos en cada carrera

    results = spark.read.csv("./datasets/results.csv", header=True,sep=",")
    for r in races_list:
        data_driver1 = results.filter( (results.raceId == r[0]) & (results.driverId == ids[0]) ).collect()
        data_driver2 = results.filter( (results.raceId == r[0]) & (results.driverId == ids[1]) ).collect()
        if (len(data_driver1) > 0):
            puntuation_driver1.append(data_driver1[0].points)
        else:
            puntuation_driver1.append(0)
        if (len(data_driver2) > 0):
            puntuation_driver2.append(data_driver2[0].points)
        else:
            puntuation_driver2.append(0)
       
    

    return list(races_list),list(names_races_list),puntuation_driver1,puntuation_driver2
#endregion

#region Numero de victorias de una temporada de un piloto


def get_num_wins_season_pilot(id):
    results = spark.read.csv("./datasets/results.csv", header=True,sep=",")
    #Obtenemos las carreras de la temporada actual
    actual_year = datetime.datetime.now().year
    races = Carrera.objects.filter(temporada=actual_year)
    count = 0
    for r in races:
        data_count = results.filter( (results.raceId == r.id) & (results.driverId == id) & (results.position == 1) ).count()
        count += data_count
    return count
#endregion



#region Evolución twitter de dos pilotos

''' Esta función devuelve la evolución de estadísticas de
     tweets de dos pilotos.
     Parámetros:
     - names: lista de dos nombres de pilotos (debe ser 2 nombres)
     Return: lista de tuplas con la siguiente estructura:
     (fecha, num_tweets, num_retweets, num_favoritos)
'''

def get_twitter_evolution(names):
    
    # Obtenemos las abreviaturas de los 2 pilotos
    abreviaturas = []
    for n in names:
        abreviaturas.append(Piloto.objects.get(apellidos = n,activo=1).abreviatura)
    
    # Obtenemos los nombres de las cuentas de twitter de los dos pilotos
    twitter_names = []
    for a in abreviaturas:
        twitter_names.append(TWITTER_PROFILE[a])
    
    # Obtenemos los datos de los tweets de los dos pilotos
    tweets_stats = spark.read.csv("./datasets/drivers_followers.csv", header=True,sep=",")



    
    # Obtenemos datos del csv del primer piloto

    data_driver1 = tweets_stats.filter(tweets_stats.Piloto == twitter_names[0])

    data_driver1 = data_driver1.withColumn("Fecha", data_driver1["Fecha"].cast(DateType()))
    data_driver1 = data_driver1.withColumn("semana", weekofyear("fecha"))
    data_driver1 = data_driver1.groupby("semana").agg(avg("Likes"),avg("Rts"),avg("Seguidores")).orderBy("semana").tail(5)
    
                      
    # Obtenemos datos del csv del segundo piloto

    data_driver2 = tweets_stats.filter(tweets_stats.Piloto == twitter_names[1])

    data_driver2 = data_driver2.withColumn("Fecha", data_driver2["Fecha"].cast(DateType()))
    data_driver2 = data_driver2.withColumn("semana", weekofyear("fecha"))

    data_driver2 = data_driver2.groupby("semana").agg(avg("Likes"),avg("Rts"),avg("Seguidores")).orderBy("semana").tail(5)
    

    #Convertimos a lista
    likes_1 = []
    rts_1 = []
    seguidores_1 = []
    likes_2 = []
    rts_2 = []
    seguidores_2 = []
    
    print (data_driver1)

    for d1,d2 in zip(data_driver1,data_driver2):
        likes_1.append(d1["avg(Likes)"])
        rts_1.append(d1["avg(Rts)"])
        seguidores_1.append(d1["avg(Seguidores)"])
        likes_2.append(d2["avg(Likes)"])
        rts_2.append(d2["avg(Rts)"])
        seguidores_2.append(d2["avg(Seguidores)"])
    

    

    
    

    return likes_1,rts_1,seguidores_1,likes_2,rts_2,seguidores_2
    
#endregion Evolución twitter de dos pilotos

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

