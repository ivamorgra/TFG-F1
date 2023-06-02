import csv 
from csv import writer
from .models import Circuito, Piloto, Constructor
from pyspark import SparkContext
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum,avg, weekofyear, count, desc, asc
from pyspark.sql.types import DateType
from django.db.models import Q
import datetime
from .models import Carrera


''' Diccionario clave -> abreviatura, valor -> nombre de usuario en twitter'''
TWITTER_PROFILE = {'Mercedes': 'MercedesAMGF1', 'Alpine':'AlpineF1Team','Haas':'HaasF1Team',
                   'McLaren':'McLarenF1','Alfa':'alfaromeof1','Williams':'WilliamsRacing','Red Bull':'redbullracing',
                   'Aston Martin':'AstonMartinF1','Ferrari':'ScuderiaFerrari','AlphaTauri':'AlphaTauriF1'}


spark = SparkSession.Builder().appName("F1Analytics").getOrCreate()

#region Comparativa de equipos (función principal)

def get_teams_comparison(names):
    ''' Abreviaturas debe ser una lista de 2 abreviaturas
    correspondiente a dos pilotos'''

    id_team1 = get_active_team_byname(names[0])
    id_team2 = get_active_team_byname(names[1])

    '''
    id_team1 = team_1.id
    id_team2 = team_2.id
    '''

    season = datetime.datetime.now().year


    # Obtenemos el número de victorias de cada equipo en la temporada
    
    season_wins1 = get_team_wins_by_season(id_team1,season)
    season_wins2 = get_team_wins_by_season(id_team2,season)
    
    
    #Obtenemos la posición más alta del equipo en la temporada
    max_pos1 = get_team_max_position_by_season(id_team1,season)
    max_pos2 = get_team_max_position_by_season(id_team2,season)
    
    #Obtenemos la posición más baja del piloto en la temporada
    min_pos1 = get_team_min_position_by_season(id_team1,season)
    min_pos2 = get_team_min_position_by_season(id_team2,season)

    
    # Obtenemos la puntuación total de cada piloto en la temporada
    total_puntuation1 = get_team_total_points_by_season(id_team1,season)
    total_puntuation2 = get_team_total_points_by_season(id_team2,season)
    

    ### ESTADÍSTICAS GLOBALES ###

    # Obtenemos el número de carreras totales
    num_carreras1 = team_num_carreras(id_team1)
    num_carreras2 = team_num_carreras(id_team2)

    
    # Obtenemos el número de victorias totales
    num_victorias1 = get_num_wins_team(id_team1)
    num_victorias2 = get_num_wins_team(id_team2)
    
    
    #Obtenemos la puntuación total de cada piloto
    total_global_puntuation1 = get_team_total_puntuation(id_team1)
    total_global_puntuation2 = get_team_total_puntuation(id_team2)
    
    
    #Obtenemos el pipeline de la temporada
    team_ids = [id_team1,id_team2]
    races_list,names_races_list,puntuation_team1,puntuation_team2 = get_comparation_team_evolution(team_ids)
    

    #Obtener datos de abandonos en las carreras en cada año
    years1,abandonos1 = get_team_crash_by_season(id_team1)
    years2,abandonos2 = get_team_crash_by_season(id_team2)

    res = {
        'years1': years1,
        'years2': years2,
        'abandonos1': abandonos1,
        'abandonos2': abandonos2,
        'avg_total_puntuation1': total_global_puntuation1/num_carreras1,
        'avg_total_puntuation2': total_global_puntuation2/num_carreras2,
        'global_puntuation1': total_global_puntuation1,
        'global_puntuation2': total_global_puntuation2,
        'num_carreras1': num_carreras1,
        'num_carreras2': num_carreras2,
        'num_victorias1': num_victorias1,
        'num_victorias2': num_victorias2,
        'total_puntuation1': total_puntuation1,
        'total_puntuation2': total_puntuation2,
        'min_pos1': min_pos1,
        'min_pos2': min_pos2,
        'max_pos1': max_pos1,
        'max_pos2': max_pos2,
        'season_wins1': season_wins1,
        'season_wins2': season_wins2,
        'races_list':races_list,
        'names_races_list': names_races_list,
        'puntuation_team1': puntuation_team1,
        'puntuation_team2': puntuation_team2
    }

    return res

#endregion


#region Obtener los abandonos por año de un equipo

def get_team_crash_by_season(id_team):
    ''' Obtiene los abandonos por año de un equipo por cada año
    que ha participado en la F1.
    Parámetros:	
    id_team (int): id del equipo
    Devuelve:
    abandonos (list): lista de abandonos por año'''

    # Hacer un join con la tabla de carreras para filtrar por año
    results = spark.read.csv("./datasets/results.csv", header=True,sep=",")
    season_races = spark.read.csv("./datasets/races.csv", header=True,sep=",")
    
    # Definición de join
    join = [results.raceId == season_races.raceId]

    # Realizar join
    results_join = results.join(season_races, join, "inner")

    # Filtrar por id del equipo y por abandonos
    results_join = results_join.filter(results_join.constructorId == id_team).filter(results_join.statusId != 1)
    #agrupamos por año y contamos los abandonos de ese año
    results_join = results_join.groupBy("year").count().orderBy(desc("year")).collect()
    #Obtenemos los años en los que ha participado el equipo
    years = [int(x.year) for x in results_join]
    #Obtenemos los abandonos en cada año
    abandonos = [int(x['count']) for x in results_join]

    return years,abandonos

#endregion Obtener los abandonos por año de un equipo

# region Obtener el equipo a partir de un nombre

def get_active_team_byname(team_name):
    """
    Obtiene el id de un equipo activo por su nombre
    """
    team = Constructor.objects.filter(Q(nombre__icontains=team_name), activo=1).get()
    if team:
        return team.id
    else:
        return None
    
# endregion


#region Obtener la posición más alta de un equipo en una temporada

def get_team_max_position_by_season(id_team,season):
    ''' Función que devuelve la posición más alta de un equipo 
        en una temporada.
        Parámetros:
            id_team: id del equipo
            season: temporada (año)
    '''

    # Hacer un join con la tabla de carreras para filtrar por año
    results = spark.read.csv("./datasets/results.csv", header=True,sep=",")
    season_races = spark.read.csv("./datasets/races.csv", header=True,sep=",")
    
    # Definición de join
    join = [results.raceId == season_races.raceId]

    # Realizar join -> nuevo dataframe unido
    results_join = results.join(season_races, join, "inner")

    num_races = results_join.filter( (results_join.constructorId == id_team) & (results_join.year == season))

    position = num_races.orderBy(asc("position"))

    for races in position.collect():
        if races.position != '0':
            return races.position
    
    return 'Carrera no terminada (DNF))'

#endregion Obtener la posición más alta de un equipo en una temporada

#region Obtener la posición más baja de un equipo en una temporada

def get_team_min_position_by_season(id_team,season):
    ''' Función que devuelve la posición más baja de un equipo 
        en una temporada.
        Parámetros:
            id_team : id del equipo
            season: temporada (año)
    '''

    # Hacer un join con la tabla de carreras para filtrar por año
    results = spark.read.csv("./datasets/results.csv", header=True,sep=",")
    season_races = spark.read.csv("./datasets/races.csv", header=True,sep=",")
    
    # Definición de join
    join = [results.raceId == season_races.raceId]

    # Realizar join -> nuevo dataframe unido
    results_join = results.join(season_races, join, "inner")

    num_races = results_join.filter( (results_join.constructorId == id_team) & (results_join.year == season))

    position = num_races.orderBy(desc("position"))
    for race in position.collect():
        if race.position == '0':
            return 'Carrera no terminada (DNF))'
    
    return position.collect()[0].position

#endregion Obtener la posición más baja de un equipo en una temporada

#region Obtener la puntuación total de un equipo en una temporada

def get_team_total_points_by_season(id_team,season):
    ''' Obtenemos la puntuación total de un equipo en una temporada'''
    results = spark.read.csv("./datasets/results.csv", header=True,sep=",")
    season_races = spark.read.csv("./datasets/races.csv", header=True,sep=",")
        
    # Definición de join
    join = [results.raceId == season_races.raceId]

    # Realizar join -> nuevo dataframe unido
    results_join = results.join(season_races, join, "inner")
    total_points = results_join.filter( (results_join.constructorId == id_team) & (results_join.year == season) ).select("points")
    total_points = total_points.agg(sum("points"))
    
    return total_points.collect()[0][0]

#endregion Obtener la puntuación total de un equipo en una temporada


#region Obtener victorias de un equipo por temporada

def get_team_wins_by_season(id_team, season):
    """
    Obtiene el número de victorias de un piloto en una temporada
    """
    team = Constructor.objects.get(id=id_team)
    if team:
        results = spark.read.csv("./datasets/results.csv", header=True,sep=",")
        season_races = spark.read.csv("./datasets/races.csv", header=True,sep=",")

        # Definicion de join
        join = [results.raceId == season_races.raceId]

        results_join = results.join(season_races, join, "inner")

        wins = results_join.filter( (results_join.constructorId == id_team) & (results_join.position == 1) & (results_join.year == season)).count()

        return wins
    else:
        return None
    
# endregion Obtener victorias de un equipo por temporada


#region Obtener el pipeline de un equipo en la temporada

def get_comparation_team_evolution(ids):
    ''' LOS PARÁMETROS SON:
    - Ids de los 2 equipos
    RETURN: Carreras de la temporada, listas de puntos de los 2 equipos'''
    
    puntuation_team1 = []
    puntuation_team2 = []

    #Obtenemos la fecha actual
    actual_date = datetime.datetime.now()
    #Obtenemos el año actual
    actual_year = actual_date.year

    #Obtenemos las carreras hasta la fecha
    races = Carrera.objects.filter(temporada=actual_year).order_by('fecha')
    #Pasamos las carreras a un array de python
    races_list = races.values_list('id')
    names_races_list = races.values_list('nombre')
    
    
    #Obtenemos los puntos de los equipos en cada carrera

    results = spark.read.csv("./datasets/results.csv", header=True,sep=",")
    for r in races_list:
        data_team1 = results.filter( (results.raceId == r[0]) & (results.constructorId == ids[0]) ).collect()
        data_team2 = results.filter( (results.raceId == r[0]) & (results.constructorId == ids[1]) ).collect()
        if (len(data_team1) > 0):
            puntuation_team1.append(data_team1[0].points)
        else:
            puntuation_team1.append(0)
        if (len(data_team2) > 0):
            puntuation_team2.append(data_team2[0].points)
        else:
            puntuation_team2.append(0)
       
    

    return list(races_list),list(names_races_list),puntuation_team1,puntuation_team2

#endregion Obtener el pipeline de un equipo en la temporada
### ESTADÍSTICAS GLOBALES ###

#region Obtener el número de carreras de un equipo

def team_num_carreras(id_team):
    ''' Obtenemos el número de carreras de un equipo'''
    results = spark.read.csv("./datasets/results.csv", header=True,sep=",")
    num_carreras = results.filter(results.constructorId == id_team).select("raceId").distinct().count()
    return num_carreras

#endregion Obtener el número de carreras de un equipo

#region Obtener el número de victorias de un equipo

def get_num_wins_team(id_team):
    ''' Función que devuelve el número de victorias 
    de un equipo en toda su trayectoria.
    Parámetros:
        id_team: id del equipo
    '''
    results = spark.read.csv("./datasets/results.csv", header=True,sep=",")
    num_wins = results.filter( (results.constructorId == id_team) & (results.position == 1)).count()
    return num_wins

#endregion Obtener el número de victorias de un equipo

#region Obtener la puntuaación total de un equipo

def get_team_total_puntuation(id_team):
    ''' Obtenemos la puntuación total de un equipo'''
    results = spark.read.csv("./datasets/results.csv", header=True,sep=",")
    total_points = results.filter(results.constructorId == id_team).select("points")
    total_points = total_points.agg(sum("points"))
    
    return total_points.collect()[0][0]

#endregion Obtener la puntuación total de un equipo

#region Evolución twitter de dos equipos

''' Esta función devuelve la evolución de estadísticas de
     tweets de dos equipos.
     Parámetros:
     - names: lista de dos nombres de equipos (debe ser 2 nombres)
     Return: lista de tuplas con la siguiente estructura:
     (fecha, num_tweets, num_retweets, num_favoritos)
'''

def get_twitter_team_evolution(names):
    
    
    # Obtenemos los nombres de las cuentas de twitter de los dos pilotos
    twitter_names = []
    for a in names:
        if (a == "Red"):
            a = "Red Bull"
        if (a == "Aston"):
            a = "Aston Martin"
        twitter_names.append(TWITTER_PROFILE[a])
    
    # Obtenemos los datos de los tweets de los dos pilotos
    tweets_stats = spark.read.csv("./datasets/followers.csv", header=True,sep=",")

    
    # Obtenemos datos del csv del primer equipo

    data_team1 = tweets_stats.filter(tweets_stats.Escuderia == twitter_names[0])

    data_team1 = data_team1.withColumn("Fecha", data_team1["Fecha"].cast(DateType()))
    data_team1 = data_team1.withColumn("semana", weekofyear("fecha"))
    data_team1 = data_team1.groupby("semana").agg(avg("Likes"),avg("Rts"),avg("Seguidores")).orderBy("semana").tail(5)
    
                      
    # Obtenemos datos del csv del segundo equipo

    data_team2 = tweets_stats.filter(tweets_stats.Escuderia == twitter_names[1])

    data_team2 = data_team2.withColumn("Fecha", data_team2["Fecha"].cast(DateType()))
    data_team2 = data_team2.withColumn("semana", weekofyear("fecha"))

    data_team2 = data_team2.groupby("semana").agg(avg("Likes"),avg("Rts"),avg("Seguidores")).orderBy("semana").tail(5)
    

    #Convertimos a lista
    likes_1 = []
    rts_1 = []
    seguidores_1 = []
    likes_2 = []
    rts_2 = []
    seguidores_2 = []
    

    for d1,d2 in zip(data_team1,data_team2):
        likes_1.append(d1["avg(Likes)"])
        rts_1.append(d1["avg(Rts)"])
        seguidores_1.append(d1["avg(Seguidores)"])
        likes_2.append(d2["avg(Likes)"])
        rts_2.append(d2["avg(Rts)"])
        seguidores_2.append(d2["avg(Seguidores)"])
    
    return likes_1,rts_1,seguidores_1,likes_2,rts_2,seguidores_2
    
#endregion Evolución twitter de dos equipos