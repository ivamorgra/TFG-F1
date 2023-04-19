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

spark = SparkSession.Builder().appName("F1Analytics").getOrCreate()

#region Comparativa de equipos (función principal)

def get_teamss_comparison(names):
    ''' Abreviaturas debe ser una lista de 2 abreviaturas
    correspondiente a dos pilotos'''
    team_1 = get_active_team_byname(names[0])
    team_2 = get_active_team_byname(names[1])

    id_team1 = team_1.id
    id_team2 = team_2.id

    season = datetime.datetime.now().year
    '''
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
'''
#endregion

# region Obtener el equipo a partir de un nombre
def get_active_team_byname(team_name):
    """
    Obtiene el id de un equipo activo por su nombre
    """
    team = Constructor.objects.get(name_icontains=team_name, active=True)
    if team:
        return team[0].id
    else:
        return None
    
# endregion