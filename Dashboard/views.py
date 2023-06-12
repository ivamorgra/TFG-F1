import datetime
from django.shortcuts import render, redirect
from django.conf import settings
#from DataAnalytics.twitter import UserClient
from DataAnalytics.trends import search_trends
from DataAnalytics.bstracker import get_standings,get_standings_teams,drivers_scrapping,constructors_scrapping, next_race_scrapping
from DataAnalytics.spark_queries import get_avg_conditions, get_avg_hum, get_evolution_temp, get_last_twitter_stats, get_meteo_byseason, get_top3drivers_evolution,get_top3teams_evolution,get_season_progress,get_pilots_comparison,get_twitter_evolution, process_confusion_matrix, process_predictions
from DataAnalytics.spark_queries_teams import get_teams_comparison,get_twitter_team_evolution
from Dashboard.model import train_model
import logging
import json

# Create your views here.


''' VISTA PRINCIPAL '''
def get_dashboard(request):

    ''' PRIMERA GRÁFICA DE GOOGLE TRENDS  
    opciones de días:
    - 365 días
    - 7 días
    - 30 días
    '''

    meses,valores,media,total,countries,values = search_trends('F1',30)
    dias_5,valores_5,media_5,total_5,countries_5,values_5 = search_trends('F1',7)
    #dias_15,valores_15,media_15,total_15,countries_15,values_15 = search_trends('F1',15)

    json_data = json.dumps(valores)
    json_data_months = json.dumps(meses)

    json_data_graph2 = json.dumps(valores_5)
    json_data_dias2 = json.dumps(dias_5)

    #json_data_graph3 = json.dumps(valores_15)
    #json_data_dias3 = json.dumps(dias_15)

    json_data_countries = json.dumps(countries)
    json_data_values = json.dumps(values)

    ''' TABLA DE CLASIFICACIÓN'''
    clasification_data,nombres,puntos = get_standings()
    clasification_data_teams,nombres_teams,puntos_teams = get_standings_teams()

    names_param = [nombres[0][2],nombres[1][2],nombres[2][2]]
    names_teams_param = [nombres_teams[0][2],nombres_teams[1][2],nombres_teams[2][2]]

        
    ''' GRÁFICA EVOLUTIVA TOP 3 PILOTOS '''

    aux_races_list,races_list,p1,p2,p3 = get_top3drivers_evolution(names_param)
    
    t1,t2,t3 = get_top3teams_evolution(names_teams_param)

    json_data_races = json.dumps(races_list)
    json_data_p1 = json.dumps(p1)
    json_data_p2 = json.dumps(p2)
    json_data_p3 = json.dumps(p3)
    json_data_nombres = json.dumps(names_param)

    ''' GRÁFICA EVOLUTIVA TOP 3 EQUIPOS  '''
    json_data_names_teams = json.dumps(names_teams_param)
    json_data_t1 = json.dumps(t1)
    json_data_t2 = json.dumps(t2)
    json_data_t3 = json.dumps(t3)

    ''' GRÁFICA DE EVOLUCIÓN DE PUNTOS'''
    context = {
        'json_data_names_teams': json_data_names_teams,
        'json_data_t1':json_data_t1,
        'json_data_t2':json_data_t2,
        'json_data_t3':json_data_t3,
        'json_data_countries':json_data_countries,
        'json_data_values':json_data_values,
        'json_data_races':json_data_races,
        'json_data_p1':json_data_p1,
        'json_data_p2':json_data_p2,
        'json_data_p3':json_data_p3,
        'json_data_nombres':json_data_nombres,
        'json_data_graph2':json_data_graph2,
        'json_data_dias2':json_data_dias2,
        #'json_data_graph3':json_data_graph3,
        #'json_data_dias3':json_data_dias3,
        'json_data_months':json_data_months,
        'values_trend':json_data,
        'STATIC_URL':settings.STATIC_URL
    }
    

    return render(request, 'dashboard/dashboard.html',context)


#region Vista de estadísticas

def get_stats(request):

    
    mostrar_preloader = True

    percentage_progress = get_season_progress()
    
    json_data_progress = json.dumps(percentage_progress)
    
    active_drivers = drivers_scrapping()
    active_teams = constructors_scrapping()

    if request.method == 'POST':

        ''' En esta vista hay 2 formularios de búsqueda, uno para comparar pilotos y 
        otro para comparar equipos'''

        if (request.POST.get('driver1') != None):
            #Se obtiene los nombres de los pilotos a comparar
            driver_1 = request.POST.get('driver1')
            driver_2 = request.POST.get('driver2')
            if (driver_2 == 'De'):
                driver_2 = "De Vries"
            
            names = [driver_1,driver_2]
            res = get_pilots_comparison(names)
            likes_1,rts_1,seguidores_1,likes_2,rts_2,seguidores_2 = get_twitter_evolution(names)
            
            team_1 = 'Red Bull'
            team_2 = 'Aston Martin'
            team_names = [team_1,team_2]
            team_res = get_teams_comparison(team_names)
            likes_e1,rts_e1,seguidores_e1,likes_e2,rts_e2,seguidores_e2 = get_twitter_team_evolution(team_names)

            
        else:
            team_1 = request.POST.get('team1')
            team_2 = request.POST.get('team2')
            team_names = [team_1,team_2]
            driver_1 = 'Verstappen'
            driver_2 = 'Alonso'

            names = [driver_1,driver_2]
            res = get_pilots_comparison(names)
            likes_1,rts_1,seguidores_1,likes_2,rts_2,seguidores_2 = get_twitter_evolution(names)

            team_res = get_teams_comparison(team_names)
            likes_e1,rts_e1,seguidores_e1,likes_e2,rts_e2,seguidores_e2 = get_twitter_team_evolution(team_names)
        

    else:
        team_1 = 'Red Bull'
        team_2 = 'Aston Martin'
        driver_1 = 'Verstappen'
        driver_2 = 'Alonso'
        
        names = [driver_1,driver_2]
        res = get_pilots_comparison(names)
        likes_1,rts_1,seguidores_1,likes_2,rts_2,seguidores_2 = get_twitter_evolution(names)

        # En el caso de los equipos:
        team_names = [team_1,team_2]
        team_res = get_teams_comparison(team_names)
        likes_e1,rts_e1,seguidores_e1,likes_e2,rts_e2,seguidores_e2 = get_twitter_team_evolution(team_names)
        
    races_list = res['races_list']
    names_races = res['names_races_list']
    payload_driver1 = res['puntuation_driver1']
    payload_driver2 = res['puntuation_driver2']

    payload_team1 = team_res['puntuation_team1']
    payload_team2 = team_res['puntuation_team2']
    
    #Datos de la gráfica de abandonos
    abandonos_t1 = team_res['abandonos1']
    years_t1 = team_res['years1']

    abandonos_t2 = team_res['abandonos2']
    years_t2 = team_res['years2']

    #Conversión de los datos a JSON
    json_races_list = json.dumps(races_list)
    json_names_races = json.dumps(names_races)
    json_payload_driver1 = json.dumps(payload_driver1)
    json_payload_driver2 = json.dumps(payload_driver2)
    json_driver_name = json.dumps(driver_1)
    json_driver_name2 = json.dumps(driver_2)
    json_twitter_likes1 = json.dumps(likes_1)
    json_twitter_likes2 = json.dumps(likes_2)
    json_twitter_rts1 = json.dumps(rts_1)
    json_twitter_rts2 = json.dumps(rts_2)
    json_twitter_seguidores2 = json.dumps(seguidores_2)
    json_twitter_seguidores1 = json.dumps(seguidores_1)
    
    json_team1_name = json.dumps(team_1)
    json_team2_name = json.dumps(team_2)
    json_payload_team1 = json.dumps(payload_team1)
    json_payload_team2 = json.dumps(payload_team2)
    json_twitter_likes_equipos1 = json.dumps(likes_e1)
    json_twitter_likes_equipos2 = json.dumps(likes_e2)
    json_twitter_rts_equipos1 = json.dumps(rts_e1)
    json_twitter_rts_equipos2 = json.dumps(rts_e2)
    json_twitter_seguidores_equipos1 = json.dumps(seguidores_e1)
    json_twitter_seguidores_equipos2 = json.dumps(seguidores_e2)
    json_abandonos_t1 = json.dumps(abandonos_t1)
    json_years_t1 = json.dumps(years_t1)
    json_abandonos_t2 = json.dumps(abandonos_t2)
    json_years_t2 = json.dumps(years_t2)

    mostrar_preloader = False
    context = {
        'mostrar_preloader':mostrar_preloader,
        #Equipos
        'json_abandonos_t1':json_abandonos_t1,
        'json_years_t1':json_years_t1,
        'json_abandonos_t2':json_abandonos_t2,
        'json_years_t2':json_years_t2,
        'json_twitter_likes_equipos1':json_twitter_likes_equipos1,
        'json_twitter_likes_equipos2':json_twitter_likes_equipos2,
        'json_twitter_rts_equipos1':json_twitter_rts_equipos1,
        'json_twitter_rts_equipos2':json_twitter_rts_equipos2,
        'json_twitter_seguidores_equipos1':json_twitter_seguidores_equipos1,
        'json_twitter_seguidores_equipos2':json_twitter_seguidores_equipos2,
        'json_team1_name':json_team1_name,
        'json_team2_name':json_team2_name,
        'teams':active_teams,
        'team_1':team_1,
        'team_2':team_2,
        'json_payload_team1':json_payload_team1,
        'json_payload_team2':json_payload_team2,
        'team_comparations':team_res,
        # Pilotos
        'comparations':res,
        'json_twitter_likes1':json_twitter_likes1,
        'json_twitter_likes2':json_twitter_likes2,
        'json_twitter_rts1':json_twitter_rts1,
        'json_twitter_rts2':json_twitter_rts2,
        'json_twitter_seguidores2':json_twitter_seguidores2,
        'json_twitter_seguidores1':json_twitter_seguidores1,
        'json_driver_name':json_driver_name,
        'json_driver_name2':json_driver_name2,
        'driver_1':driver_1,
        'driver_2':driver_2,
        'json_races_list':json_races_list,
        'json_names_races':json_names_races,
        'json_payload_driver1':json_payload_driver1,
        'json_payload_driver2':json_payload_driver2,
        'json_data_progress':json_data_progress,
        'ad':active_drivers,
        'STATIC_URL':settings.STATIC_URL
    }
    return render(request, 'dashboard/stats.html',context)

#endregion


def get_loader(request):
    return render(request, 'loader.html')

#region Vista de Clasificación

def get_view_standings(request):

    driver_standings,names,points = get_standings()
    
    team_standings,names,points = get_standings_teams()

    context = {
        'driver_standings':driver_standings,
        'team_standings':team_standings,
    }
    return render(request, 'dashboard/standings.html',context)
#endregion Vista de Clasificación


#region Vista de Meteorología

def get_view_weather(request):
    season = datetime.datetime.now().year
    weather = get_meteo_byseason(season)
    names, temps = get_evolution_temp(season)
    avg_hum = get_avg_hum(season)
    avg_conditions = get_avg_conditions(season)

    json_names = json.dumps(names)
    json_temps = json.dumps(temps)
    json_avg_hum = json.dumps(avg_hum)
    json_avg_conditions = json.dumps(avg_conditions)

    context = {
        'weather':weather,
        'json_names':json_names,
        'json_temps':json_temps,
        'json_avg_hum':json_avg_hum,
        'json_avg_conditions':json_avg_conditions,
        'STATIC_URL':settings.STATIC_URL
    }
    return render(request, 'dashboard/weather.html',context)

#endregion Vista de Meteorología

def get_view_predictions(request):
    df,confusion_matrix,rmse  = train_model()
    res= process_predictions(df)
    confusion_matrix_list = process_confusion_matrix(confusion_matrix)
    next_race = next_race_scrapping()

    json_rmse = json.dumps(rmse)
    context = {
        'res': res,
        'race': next_race,
        'json_rmse': json_rmse,
        'matrix': confusion_matrix_list,
        'STATIC_URL':settings.STATIC_URL

    }
    return render(request, 'dashboard/predictions.html',context)

''' APARTADO TWITTER '''

def get_twitter_stats(request):

    res_drivers, res_teams = get_last_twitter_stats()

    context = {
        'drivers':res_drivers,
        'teams':res_teams,
        'STATIC_URL':settings.STATIC_URL
    }

    return render(request,'dashboard/twitter.html', context)