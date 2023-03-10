from django.shortcuts import render
from django.conf import settings
from DataAnalytics.twitter import UserClient
import logging
# Create your views here.

def get_dashboard(request):
    return render(request, 'dashboard/dashboard.html')

def get_twitter_stats(request,num):

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