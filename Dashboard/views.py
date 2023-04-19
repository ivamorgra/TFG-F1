from django.shortcuts import render
from django.conf import settings
from DataAnalytics.twitter import UserClient
from DataAnalytics.trends import search_trends
from DataAnalytics.bstracker import get_standings,get_standings_teams,drivers_scrapping
from DataAnalytics.spark_queries import get_top3drivers_evolution,get_top3teams_evolution,get_season_progress,get_pilots_comparison,get_twitter_evolution
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
    percentage_progress = get_season_progress()
    
    json_data_progress = json.dumps(percentage_progress)
    
    active_drivers = drivers_scrapping()

    if request.method == 'POST':

        #Se obtiene los nombres de los pilotos a comparar
        driver_1 = request.POST.get('driver1')
        driver_2 = request.POST.get('driver2')
        if (driver_2 == 'De'):
            driver_2 = "De Vries"
        
        names = [driver_1,driver_2]
        res = get_pilots_comparison(names)
        likes_1,rts_1,seguidores_1,likes_2,rts_2,seguidores_2 = get_twitter_evolution(names)

    else:
        driver_1 = 'Verstappen'
        driver_2 = 'Alonso'
        
        names = [driver_1,driver_2]
        res = get_pilots_comparison(names)
        likes_1,rts_1,seguidores_1,likes_2,rts_2,seguidores_2 = get_twitter_evolution(names)
    
    races_list = res['races_list']
    names_races = res['names_races_list']
    payload_driver1 = res['puntuation_driver1']
    payload_driver2 = res['puntuation_driver2']


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
        

    context = {
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

''' APARTADO TWITTER '''
def get_twitter_stats(request,num):

    ''' PÁGINA DE ESTADÍSTICAS DE TWITTER
    opciones de botones:
    - 10 últimos tweets
    - 25 últimos tweets
    - 50 últimos tweets
    '''

    ''' Activación de botones'''
    active1 = ''
    active2 = ''
    active3 = ''
    ACTIVO = ' active'
    if  num == 10:
        active1 = ACTIVO
    elif num == 25:
        active2 = ACTIVO
    elif num == 50:
        active3 = ACTIVO


    twitter_api = UserClient()

    ''' CONSTRUCTORES '''
    followers_stats = twitter_api.get_stats_constructors(num)
    
    ''' PILOTOS '''
    followers_stats_drivers = twitter_api.get_stats_drivers(num)
       
    context = {
                'active1':active1,
                'active2':active2,
                'active3':active3,
                'num':num,
                'teams':followers_stats,
                'drivers':followers_stats_drivers,
                'STATIC_URL':settings.STATIC_URL
            }
    return render(request, 'dashboard/twitter.html',{'context':context})