import matplotlib.pyplot as plt
import pandas as pd
from pytrends.request import TrendReq
from django.http import HttpResponse
from django.shortcuts import render
import datetime


MONTHS = {'01': "January", '02': 'February', '03': 'March', 
          '04': 'April', '05': 'May', '06': 'June', '07': 'July',
            '08': 'August', '09': 'September', '10': 'October',
              '11': 'November', '12': 'December'}

def search_trends(keyword):

    fecha_fin = datetime.datetime.now().strftime('%Y-%m-%d')
    fecha_inicio = (datetime.datetime.now() - datetime.timedelta(days=365)).strftime('%Y-%m-%d')
    
    #Creación de una instancia de la clase TrendReq
    pytrend = TrendReq(hl='en-US', tz=360)
    pytrend.build_payload(kw_list=[keyword], timeframe=f'{fecha_inicio} {fecha_fin}')
    #pytrend.build_payload(kw_list=[keyword], timeframe='today 5-y')
    data = pytrend.interest_over_time()
    df = data.resample('M').sum()
  
    valores = df[keyword].tolist()
    total = df[keyword].sum()
    media = df[keyword].mean()
    #interest_over_time_df = pytrend.interest_over_time()

    months = []
    
    # Obtener fechas de captura
    dates_captured = df.index.tolist()
    for date in dates_captured:
        print (date.strftime("%m"))
        months.append(MONTHS[date.strftime("%m")])
            
    return months,valores,media,total
    
