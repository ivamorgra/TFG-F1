import matplotlib.pyplot as plt
import pandas as pd
from pytrends.request import TrendReq
from django.http import HttpResponse
from django.shortcuts import render
import datetime


MONTHS = {1: "January", 2: 'February', 3: 'March', 
          4: 'April', 5: 'May', 6: 'June', 7: 'July',
            8: 'August', 9: 'September', 10: 'October',
              11: 'November', 12: 'December'}

def search_trends(keyword):

    fecha_fin = datetime.datetime.now().strftime('%Y-%m-%d')
    fecha_inicio = (datetime.datetime.now() - datetime.timedelta(days=150)).strftime('%Y-%m-%d')
    primer_mes = int(fecha_inicio.split('-')[1])
    #Creación de una instancia de la clase TrendReq
    pytrend = TrendReq(hl='en-US', tz=360)
    pytrend.build_payload(kw_list=[keyword], timeframe=f'{fecha_inicio} {fecha_fin}')
    #pytrend.build_payload(kw_list=[keyword], timeframe='today 5-y')
    data = pytrend.interest_over_time()
    df = data.resample('M').sum()
  
    valores = df[keyword].tolist()
    total = df[keyword].sum()
    media = df[keyword].mean()
    #Obtención de los valores de los ejes para construir el gráfico en la vista
    
    
   

    
    return primer_mes,valores,media,total
    
