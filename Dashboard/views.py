from django.shortcuts import render
from django.conf import settings
from DataAnalytics.twitter import UserClient
from DataAnalytics.trends import search_trends
from DataAnalytics.bstracker import get_standings,get_standings_teams
from DataAnalytics.spark_queries import get_top3drivers_evolution,get_top3teams_evolution
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

    meses,valores,media,total,countries,values = search_trends('F1',365)
    dias_5,valores_5,media_5,total_5,countries_5,values_5 = search_trends('F1',7)
    dias_15,valores_15,media_15,total_15,countries_15,values_15 = search_trends('F1',30)

    json_data = json.dumps(valores)
    json_data_months = json.dumps(meses)

    json_data_graph2 = json.dumps(valores_5)
    json_data_dias2 = json.dumps(dias_5)

    json_data_graph3 = json.dumps(valores_15)
    json_data_dias3 = json.dumps(dias_15)

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
        'json_data_graph3':json_data_graph3,
        'json_data_dias3':json_data_dias3,
        'json_data_months':json_data_months,
        'values_trend':json_data,
        'STATIC_URL':settings.STATIC_URL
    }
    

    return render(request, 'dashboard/dashboard.html',context)

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