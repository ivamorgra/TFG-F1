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

WEEK_DAYS = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday',4: 'Friday',
              5: 'Saturday', 6: 'Sunday'}



def search_trends(keyword,days):
    ''' Esta función trata de obtener los datos de tendencias de Google Trends
    
    -keyword: Palabra clave a buscar
    -days: Número de días a buscar
    
    -return: meses,valores,media,total
    (si los días no superan los meses entonces meses pasa a ser días)'''

    fecha_fin = datetime.datetime.now().strftime('%Y-%m-%d')
    fecha_inicio = (datetime.datetime.now() - datetime.timedelta(days)).strftime('%Y-%m-%d')
    
    #Creación de una instancia de la clase TrendReq
    pytrend = TrendReq(hl='en-US', tz=360)
    pytrend.build_payload(kw_list=[keyword], timeframe=f'{fecha_inicio} {fecha_fin}')
    
    data = pytrend.interest_over_time()
     
    if (days > 30):
      df = data.resample('M').sum()
      valores = df[keyword].tolist()
      total = df[keyword].sum()
      media = df[keyword].mean()
    else:
      valores = data[keyword].tolist()
      total = data[keyword].sum()
      media = data[keyword].mean()
    

    months = []
    
    if (days > 30):
    # Obtener fechas de captura
      dates_captured = df.index.tolist()
      for date in dates_captured:
          
          months.append(MONTHS[date.strftime("%m")])
    
    else:
      dates_captured = data.index.tolist()
      
      for date in dates_captured:
          
          str_date = date.strftime("%y%m%d")
          day_date = datetime.datetime.strptime(str_date, "%y%m%d").weekday()
          
          months.append(WEEK_DAYS[day_date])
            
    return months,valores,media,total



    
