import csv 
from csv import writer

import numpy as np
from collections import Counter
from F1Analytics import settings
from .models import Circuito, Piloto, Constructor
from pyspark import SparkContext
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum,avg, weekofyear, count, desc, asc
from pyspark.sql.types import DateType
from django.db.models import Q
import datetime
from .models import Carrera
from pyspark.sql.functions import to_date

spark = SparkSession.Builder().appName("F1Analytics").getOrCreate()

''' Diccionario clave -> abreviatura, valor -> nombre de usuario en twitter'''
TWITTER_PROFILE = {'HAM': 'LewisHamilton', 'ALO':'alo_oficial','BOT':'ValtteriBottas',
                   'MAG':'KevinMagnussen','VER':'Max33Verstappen','SAI':'Carlossainz55','OCO':'OconEsteban',
                   'STR':'lance_stroll','GAS':'PierreGASLY','LEC':'Charles_Leclerc','NOR':'LandoNorris','RUS':'GeorgeRussell63',
                   'ALB':'alex_albon','TSU':'yukitsunoda07','PER':'SChecoPerez','ZHO':'ZhouGuanyu24','PIA':'OscarPiastri',
                   'HUL':'HulkHulkenberg','DE ':'nyckdevries','SAR':'LoganSargeant'}


#region Obtener podium de una carrera

def get_race_podium(race_id):
    
    results = spark.read.csv("./datasets/results.csv", header=True,sep=",")

    first_driver = results.filter( (results.raceId == race_id) & (results.position == 1) ).collect()[0]
    second_driver = results.filter( (results.raceId == race_id) & (results.position == 2) ).collect()[0]
    third_driver = results.filter( (results.raceId == race_id) & (results.position == 3) ).collect()[0]

    driver_one = Piloto.objects.get(pk=int(first_driver[2]))
    second_one = Piloto.objects.get(pk=int(second_driver[2]))
    third_one = Piloto.objects.get(pk=int(third_driver[2]))

    podium = [(1,driver_one),(2,second_one),(3,third_one)]

    return podium
#endregion Obtener datos de una carrera
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

#region Obtener carreras de un piloto en una temporada

def get_driver_num_races_by_season(driver_id,season):
    ''' Función que devuelve el número de carreras de un piloto 
        en una temporada.
        Parámetros:
            driver_id: id del piloto
            season: temporada (año)
    '''

    # Hacer un join con la tabla de carreras para filtrar por año
    results = spark.read.csv("./datasets/results.csv", header=True,sep=",")
    season_races = spark.read.csv("./datasets/races.csv", header=True,sep=",")
    
    # Definición de join
    join = [results.raceId == season_races.raceId]

    # Realizar join -> nuevo dataframe unido
    results_join = results.join(season_races, join, "inner")

    num_races = results_join.filter( (results_join.driverId == driver_id) & (results_join.year == season)).count()

    return num_races


#endregion Obtener carreras de un piloto en una temporada

#region Obtener carreras de un piloto 

def get_driver_num_races(driver_id):
    ''' Función que devuelve el número de victorias de un piloto 
        en una temporada.
        Parámetros:
            driver_id: id del piloto
            season: temporada (año)
    '''

    results = spark.read.csv("./datasets/results.csv", header=True,sep=",")
    
    num_races = results.filter( (results.driverId == driver_id)).count()

    return num_races

#endregion Obtener carreras de un piloto


#region Obtener la posición habitual de un piloto en la temporada

def get_driver_avg_position_by_season(driver_id,season):
    ''' Función que devuelve la posición más habitual de un piloto 
        en una temporada.
        Parámetros:
            driver_id: id del piloto
            season: temporada (año)
    '''

    # Hacer un join con la tabla de carreras para filtrar por año
    results = spark.read.csv("./datasets/results.csv", header=True,sep=",")
    season_races = spark.read.csv("./datasets/races.csv", header=True,sep=",")
    
    # Definición de join
    join = [results.raceId == season_races.raceId]

    # Realizar join -> nuevo dataframe unido
    results_join = results.join(season_races, join, "inner")

    num_races = results_join.filter( (results_join.driverId == driver_id) & (results_join.year == season))

    positions = num_races.groupBy("position").agg(count("*").alias("count"))

    res = positions.orderBy(desc("count")).first()

    return res[0],res[1]


#endregion Obtener la posición habitual de un piloto en la temporada

#region Obtener la posición más alta de un piloto en la temporada
def get_driver_max_position_by_season(driver_id,season):
    ''' Función que devuelve la posición más alta de un piloto 
        en una temporada.
        Parámetros:
            driver_id: id del piloto
            season: temporada (año)
    '''

    # Hacer un join con la tabla de carreras para filtrar por año
    results = spark.read.csv("./datasets/results.csv", header=True,sep=",")
    season_races = spark.read.csv("./datasets/races.csv", header=True,sep=",")
    
    # Definición de join
    join = [results.raceId == season_races.raceId]

    # Realizar join -> nuevo dataframe unido
    results_join = results.join(season_races, join, "inner")

    num_races = results_join.filter( (results_join.driverId == driver_id) & (results_join.year == season))

    position = num_races.orderBy(asc("position")).first()
    
    if settings.TESTING:
        return position[0]
    else:
        return position.position

#endregion Obtener la posición más alta de un piloto en la temporada

#region Obtener la posición más baja de un piloto en la temporada
def get_driver_min_position_by_season(driver_id,season):
    ''' Función que devuelve la posición más baja de un piloto 
        en una temporada.
        Parámetros:
            driver_id: id del piloto
            season: temporada (año)
    '''

    # Hacer un join con la tabla de carreras para filtrar por año
    results = spark.read.csv("./datasets/results.csv", header=True,sep=",")
    season_races = spark.read.csv("./datasets/races.csv", header=True,sep=",")
    
    # Definición de join
    join = [results.raceId == season_races.raceId]

    # Realizar join -> nuevo dataframe unido
    results_join = results.join(season_races, join, "inner")

    num_races = results_join.filter( (results_join.driverId == driver_id) & (results_join.year == season))

    position = num_races.orderBy(desc("position")).first()
    
    if settings.TESTING:
        return position[0]
    else:
        return position.position


#endregion Obtener la posición más baja de un piloto en la temporada

#region Obtener la puntuación media de un piloto en la temporada

def get_driver_avg_points_by_season(driver_id,season):
    ''' Función que devuelve la media de la puntuación de un piloto 
        en una temporada.
        Parámetros:
            driver_id: id del piloto
            season: temporada (año)
    '''

    # Hacer un join con la tabla de carreras para filtrar por año
    results = spark.read.csv("./datasets/results.csv", header=True,sep=",")
    season_races = spark.read.csv("./datasets/races.csv", header=True,sep=",")
    
    # Definición de join
    join = [results.raceId == season_races.raceId]

    # Realizar join -> nuevo dataframe unido
    results_join = results.join(season_races, join, "inner")

    num_races = results_join.filter( (results_join.driverId == driver_id) & (results_join.year == season))

    avg_points = num_races.agg(avg("points"))

    return round(avg_points.first()[0],2)
    
#endregion Obtener la puntuación media de un piloto en la temporada

#region Obtener numero de victorias en una temporada

def get_driver_wins_by_season(driver_id,season):
        ''' Función que devuelve el número de victorias de un piloto 
            en una temporada.
            Parámetros:
                driver_id: id del piloto
                season: temporada (año)
        '''

        # Hacer un join con la tabla de carreras para filtrar por año
        results = spark.read.csv("./datasets/results.csv", header=True,sep=",")
        season_races = spark.read.csv("./datasets/races.csv", header=True,sep=",")
        
        # Definición de join
        join = [results.raceId == season_races.raceId]

        # Realizar join -> nuevo dataframe unido
        results_join = results.join(season_races, join, "inner")

        wins = results_join.filter( (results_join.driverId == driver_id) & (results_join.position == 1) & (results_join.year == season)).count()

        return wins

#endregion Obtener numero de victorias en una temporada

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
    races = races.select("raceId","name","year","date")
    races = races.withColumn('date_datetime', to_date(races.date, 'dd/MM/yy'))
    races = races.filter(races.date_datetime < datetime.datetime.now()).collect()
    
    #filter(datetime.datetime.strptime("dd/mm/yy",str(races.date)) < datetime.datetime.now()).collect()
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
    races = Carrera.objects.filter(temporada=actual_year).order_by('fecha')
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
    races = Carrera.objects.filter(temporada=actual_year).order_by('fecha') 
    races_list = races.values_list('id')

    try:
        
        team_1 = Constructor.objects.filter(Q(nombre__icontains= names[0].split(' ')[0] ), activo = 1).get()
        
        team_2 = Constructor.objects.filter(Q(nombre__icontains= names[1].split(' ')[0] ), activo = 1).get()
        team_3 = Constructor.objects.filter(Q(nombre__icontains= names[2].split(' ')[0] ), activo = 1).get()

        #Obtenemos los puntos de los equipos en cada carrera
        results = spark.read.csv("./datasets/results.csv", header=True,sep=",")
        
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

#region Obtener puntuación total de un piloto
def get_driver_total_points_by_season(id_driver,season):

    ''' Obtenemos la puntuación total de un piloto en una temporada'''
    results = spark.read.csv("./datasets/results.csv", header=True,sep=",")
    season_races = spark.read.csv("./datasets/races.csv", header=True,sep=",")
        
    # Definición de join
    join = [results.raceId == season_races.raceId]

    # Realizar join -> nuevo dataframe unido
    results_join = results.join(season_races, join, "inner")
    total_points = results_join.filter( (results_join.driverId == id_driver) & (results_join.year == season) ).select("points")
    total_points = total_points.agg(sum("points"))
    
    return total_points.collect()[0][0]

#endregion

#region Comparativa de pilotos

def get_pilots_comparison(names):
    ''' Abreviaturas debe ser una lista de 2 abreviaturas
    correspondiente a dos pilotos'''
    driver_1 = get_active_driver_byname(names[0])
    driver_2 = get_active_driver_byname(names[1])

    id_driver1 = driver_1.id
    id_driver2 = driver_2.id

    season = datetime.datetime.now().year

    # Número de carreras de la temporada
    num_carreras_1 = get_driver_num_races_by_season(id_driver1,season)
    num_carreras_2 = get_driver_num_races_by_season(id_driver2,season)
    # Obtenemos el número de victorias de cada piloto en la temporada
    
    season_wins1 = get_driver_wins_by_season(id_driver1,season)
    season_wins2 = get_driver_wins_by_season(id_driver2,season)

    #Obtenemos posición habitual del piloto en la temporada
    avg_pos1 = get_driver_avg_position_by_season(id_driver1,season)
    avg_pos2 = get_driver_avg_position_by_season(id_driver2,season)
    
    #Obtenemos la posición más alta del piloto en la temporada
    max_pos1 = get_driver_max_position_by_season(id_driver1,season)
    max_pos2 = get_driver_max_position_by_season(id_driver2,season)

    #Obtenemos la posición más baja del piloto en la temporada
    min_pos1 = get_driver_min_position_by_season(id_driver1,season)
    min_pos2 = get_driver_min_position_by_season(id_driver2,season)

    # Obtenemos la puntuación total de cada piloto en la temporada
    total_puntuation1 = get_driver_total_points_by_season(id_driver1,season)
    total_puntuation2 = get_driver_total_points_by_season(id_driver2,season)
    #Obtenemos la media de las puntuaciones de un piloto en la temporada
    avg_puntuation1 = get_driver_avg_points_by_season(id_driver1,season)
    avg_puntuation2 = get_driver_avg_points_by_season(id_driver2,season)

    ### ESTADÍSTICAS GLOBALES ###
    # Obtenemos el número de victorias de cada piloto en la temporada
    max_wins1 = get_driver_max_wins_one_season(id_driver1)
    max_wins2 = get_driver_max_wins_one_season(id_driver2)

    # Obtenemos el número de carreras totales
    num_carreras1 = driver_num_carreras(id_driver1)
    num_carreras2 = driver_num_carreras(id_driver2)

    # Obtenemos el número de victorias totales
    num_victorias1 = get_num_wins_driver(id_driver1)
    num_victorias2 = get_num_wins_driver(id_driver2)

    # Obtenemos el número de veces que no acabó un piloto una carrera
    num_no_finish1 = driver_num_no_finish(id_driver1)
    num_no_finish2 = driver_num_no_finish(id_driver2)

    # Obtener la puntuación media de un piloto
    avg_total_puntuation1 = get_driver_average_puntuation(id_driver1)
    avg_total_puntuation2 = get_driver_average_puntuation(id_driver2)

    #Obtenemos la puntuación total de cada piloto
    total_global_puntuation1 = get_driver_total_puntuation(id_driver1)
    total_global_puntuation2 = get_driver_total_puntuation(id_driver2)

    #Obtenemos la posición habitual de cada piloto
    avg_global_pos1, count1 = get_driver_habitual_position(id_driver1)
    avg_global_pos2, count2 = get_driver_habitual_position(id_driver2)

    #Obtenemos el pipeline de la temporada
    ids = [id_driver1,id_driver2]
    races_list,names_races_list,puntuation_driver1,puntuation_driver2 = get_comparation_drivers_evolution(ids)

    res = {
        'avg_count1':count1,
        'avg_count2':count2,
        'avg_global_pos1': avg_global_pos1,
        'avg_global_pos2': avg_global_pos2,
        'global_puntuation1': total_global_puntuation1,
        'global_puntuation2': total_global_puntuation2,
        'avg_total_puntuation1': avg_total_puntuation1,
        'avg_total_puntuation2': avg_total_puntuation2,
        'num_carreras1': num_carreras1,
        'num_carreras2': num_carreras2,
        'num_victorias1': num_victorias1,
        'num_victorias2': num_victorias2,
        'num_no_finish1': num_no_finish1,
        'num_no_finish2': num_no_finish2,
        'total_puntuation1': total_puntuation1,
        'total_puntuation2': total_puntuation2,
        'season_races1': num_carreras_1,
        'season_races2': num_carreras_2,
        'avg_puntuation1': avg_puntuation1,
        'avg_puntuation2': avg_puntuation2,
        'min_pos1': min_pos1,
        'min_pos2': min_pos2,
        'max_pos1': max_pos1,
        'max_pos2': max_pos2,
        'avg_pos1': avg_pos1[0],
        'avg_pos2': avg_pos2[0],
        'max_wins_season1': max_wins1[0],
        'max_wins_driver1': max_wins1[1],
        'max_wins_season2': max_wins2[0],
        'max_wins_driver2': max_wins2[1],
        'season_wins1': season_wins1,
        'season_wins2': season_wins2,
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
    races = Carrera.objects.filter(temporada=actual_year).order_by('fecha')
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


'''############## ESTADÍSTICAS GLOBALES DE UN PILOTO ##############'''

#region Numero de victorias  de un piloto
def get_num_wins_driver(id):
    results = spark.read.csv("./datasets/results.csv", header=True,sep=",")
    #Obtenemos el número de victorias de un piloto
    data_count = results.filter( (results.driverId == id) & (results.position == 1) ).count()
    
    return data_count
#endregion

#region Numero de carreras de un piloto

def driver_num_carreras(id):
    results = spark.read.csv("./datasets/results.csv", header=True,sep=",")
    #Obtenemos el número de carreras de un piloto
    data_count = results.filter( results.driverId == id ).count()
    
    return data_count
#endregion

#region Numero de veces que un piloto no ha acabado una carrera

def driver_num_no_finish(id):
    results = spark.read.csv("./datasets/results.csv", header=True,sep=",")
    #Obtenemos el número de carreras de un piloto
    data_count = results.filter( (results.driverId == id) & (results.statusId != 1) ).count()
    
    return data_count

#endregion Numero de veces que un piloto no ha acabado una carrera

#region Obtener el mayor número de victorias en una temporada

def get_driver_max_wins_one_season(driver_id):
    ''' Función que devuelve el mayor número de victorias de un piloto 
        en una temporada.
        Parámetros:
            driver_id: id del piloto
    '''

    # Hacer un join con la tabla de carreras para filtrar por año
    results = spark.read.csv("./datasets/results.csv", header=True,sep=",")
    season_races = spark.read.csv("./datasets/races.csv", header=True,sep=",")
    
    # Definición de join
    join = [results.raceId == season_races.raceId]

    # Realizar join -> nuevo dataframe unido
    results_join = results.join(season_races, join, "inner")

    #Primero filtramos por victorias del piloto
    races_by_season = results_join.filter( (results_join.driverId == driver_id) & (results_join.position == 1))

    # Agrupamos las victorias por año y las contamos
    result = races_by_season.groupBy("year").agg(count("*").alias("count"))
    result.show()
    res = result.orderBy(desc("count")).first()

    if (res is None):
        year = 0
        num_wins = 0
    else:
        year = res[0]
        num_wins = res[1]

    return [year,num_wins]
    
#endregion Obtener el mayor número de victorias en una temporada

#region Obtener la puntuación media de un piloto

def get_driver_average_puntuation(driver_id):
    ''' Función que devuelve la puntuación media de un piloto.
        Parámetros:
            driver_id: id del piloto
    '''

    results = spark.read.csv("./datasets/results.csv", header=True,sep=",")
    #Obtenemos la puntuación media de un piloto
    data = results.filter( results.driverId == driver_id ).agg(avg("points"))
    
    return round(data.first()[0],2)

#endregion Obtener la puntuación media de un piloto

#region Obtener la puntuación total de un piloto

def get_driver_total_puntuation(driver_id):
    ''' Función que devuelve la puntuación total de un piloto.
        Parámetros:
            driver_id: id del piloto
    '''

    results = spark.read.csv("./datasets/results.csv", header=True,sep=",")
    #Obtenemos la puntuación total de un piloto
    data = results.filter( results.driverId == driver_id ).agg(sum("points"))
    
    return data.first()[0]

#endregion Obtener la puntuación total de un piloto

#region Obtener la pos habitual de un piloto

def get_driver_habitual_position(driver_id):
    ''' Función que devuelve la posición habitual de un piloto.
        Parámetros:
            driver_id: id del piloto
    '''

    results = spark.read.csv("./datasets/results.csv", header=True,sep=",")
    #Obtenemos la posición habitual de un piloto
    positions = results.filter(results.driverId == driver_id).groupBy("position").agg(count("*").alias("count"))

    res = positions.orderBy(desc("count")).collect()


    if res[0][0] == "\\N":
        return res[1][0] , res[1][1]
    else:
        return res[0][0], res[0][1]
    
#endregion Obtener la pos habitual de un piloto
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



#region Obtener datos de meteorología de una temporada
def get_meteo_byseason(year):
    ''' Obtenemos los datos de meteorología de una temporada'''
    res = []
    meteo = spark.read.csv("./datasets/meteo.csv", header=True,sep=",")
    meteo = meteo.filter(meteo.temporada == year).collect()
    for m in meteo:
        nombre = m["nombre"]
        temp_min = m["min_temp"]
        temp = m["temperatura"]
        humedad = m["humedad"]
        precipitaciones = m["precipitacion"]
        condiciones = m["condiciones"]
        res.append((nombre,temp_min,temp,humedad,precipitaciones,condiciones))
    return res
#endregion Obtener datos de meteorología de una temporada
#region Obtener evolución de la temperatura de una temporada
def get_evolution_temp(season):
    ''' Obtenemos la evolución de la temperatura a lo largo de la temporada'''
    names = []
    temps = []
    meteo = spark.read.csv("./datasets/meteo.csv", header=True,sep=",")
    meteo = meteo.filter(meteo.temporada == season).collect()
    for m in meteo:
        nombre = m["nombre"]
        temp = m["temperatura"]
        names.append(nombre)
        temps.append(temp)
    return names, temps
#endregion Obtener evolución de la temperatura de una temporada
#region Obtener media de la humedad de una temporada
def get_avg_hum(season):
    ''' Obtenemos la media de la humedad a lo largo de la temporada'''
    hums = []
    meteo = spark.read.csv("./datasets/meteo.csv", header=True,sep=",")
    meteo = meteo.filter(meteo.temporada == season).collect()
    for m in meteo:
        hum = float(m["humedad"])
        hums.append(hum)
    return np.mean(hums)
#endregion Obtener media de la humedad de una temporada
#region Obtener condiciones de una temporada

def get_avg_conditions(season):
    ''' Obtenemos la media de las condiciones a lo largo de la temporada'''
    meteo = spark.read.csv("./datasets/meteo.csv", header=True,sep=",")
    meteo = meteo.filter(meteo.temporada == season)
    
    ''' Obtenemos el número de carreras que hay en la temporada'''

    num_races = meteo.count()


    conds = ['Rain','Clear','cloudy']
    res = []

    for c in conds:
        value = meteo.filter(col("condiciones").like("%{}%".format(c))).count() / num_races
        res.append(value)

    return res
#endregion Obtener condiciones de una temporada


#region Procesamiento del dataframe de predicciones
def process_predictions(df): 
    
    count_df = df.count()
    distinct_df = df.select("prediction","forename","surname", "probability").dropDuplicates(["prediction", "forename"])
    
    count_ddf= distinct_df.count()

    sorted_df = distinct_df.orderBy(distinct_df["prediction"].asc())  # Orden descendente
    sorted_df.show()
    res = []
    for row in sorted_df.collect():
        predict = [
            int(row['prediction']) if int(row['prediction']) != 0 else 'DNF',
            row['forename'],
            row['surname']
        ]
        array_probability = list(row['probability'])
        probability = int(array_probability[int(row['prediction'])])
        res_prob = 'Alta'
        if (probability < 0.5):
            res_prob = 'Baja'
        predict.append(res_prob)
        
        res.append(predict)

    
    return  sorted(res, key=lambda x: (isinstance(x[0], int), x[0]))

    #return res
#endregion Procesamiento del dataframe de predicciones

#region Procesar dataframe de matriz de confusión

def process_confusion_matrix(df):
    res = []
    for row in df.collect():
        res.append((
            row['position'],
            row['total_instances'],
            row['correct_instances'],
            row['precision'],
            row['recall'],
            row['f1_score']
        ))
    return res
#endregion Procesar dataframe de matriz de confusión


def get_last_twitter_stats():

    twitter_drivers = spark.read.csv('./datasets/drivers_followers.csv', header=True)
    twitter_teams = spark.read.csv('./datasets/followers.csv', header=True)

    df_last = twitter_drivers.orderBy(twitter_drivers.Fecha).limit(10).collect()
    df_last_teams = twitter_teams.orderBy(twitter_teams.Fecha).limit(20).collect()
    
    driver_res = []
    team_res = []

    for row in df_last:
        driver_res.append([row["Piloto"],row["Seguidores"],row["Tweets"],row["Likes"],row["Rts"]])
    
    for row in df_last_teams:
        #team_res.append((row["Escuderia"],row["Seguidores"],row["Tweets"],row["Likes"],row["Rts"]))
        team_res.append([row["Escuderia"],row["Seguidores"],row["Tweets"],row["Likes"],row["Rts"]])

    return driver_res, team_res
