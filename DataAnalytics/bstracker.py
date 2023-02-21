from bs4 import BeautifulSoup
import urllib.request, urllib.parse, urllib.error
import datetime
from pyspark import SparkContext
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
import csv

spark = SparkSession.Builder().appName("F1Analytics").getOrCreate()

URL_F1_OFFICIAL = 'https://www.formula1.com/'


MONTHS = {'Jan':'01','Feb':'02','Mar':'03','Apr':'04','May':'05',
'Jun':'06','Jul':'07','Aug':'08','Sep':'09','Oct':'10',
'Nov':'11','Dec':'12'}
'''
MONTHS = {'01':'Jan','02':'Feb','03':'Mar','04':'Apr',
'05':'May','06':'Jun','07':'Jul','08':'Aug','09':'Sep',
'10':'Oct','11':'Nov','12':'Dec'}
'''
def race_scrapping(url):
    podium = []
    count = 0
    #circuit_name = ''
    f = urllib.request.urlopen(url)
    
    soup = BeautifulSoup(f,"html.parser")
    data = soup.find_all('table', class_ = "infobox vevent")
    for row in data:
        #circuit_name = row.find('td', class_ = "infobox-data location").text
        data_podium = row.find_all('div', class_ = "plainlist")
        for li in data_podium:
            podium.append((count,li.find_all('a')[-1].get('title')))
            count += 1
    pole_position = podium[0][1]
    
    return  podium[1:],pole_position


def next_race_scrapping():

    next_races = spark.read.csv('./datasets/next_races.csv', header=True,sep=",")
    
    actual_date = datetime.datetime.now()

    year = actual_date.year
    month = actual_date.month
    day = actual_date.day

    list_races = next_races.filter(next_races.temporada == year).collect()

    #Si no hay ninguna carrera registrada para este año, se obtienen las fechas de la web oficial
    if(len(list_races) == 0):
        new_races = []
        with open("./datasets/next_races.csv", "a",newline='') as f:
            writer = csv.writer(f)
    
            url = URL_F1_OFFICIAL + '/en/racing/'+str(year)+'.html'

            f = urllib.request.urlopen(url)
            
            soup = BeautifulSoup(f,"html.parser")

            # Obtenemos la carta de eventos de este año
            event_card = soup.find_all('fieldset',class_= "race-card-wrapper event-item")
            for event in event_card:
                ronda = event.find('legend').text
                fechas = event.find_all('span')
                
                fecha_comienzo = fechas[1].text
                fecha_fin = fechas[2].text
                mes = fechas[3].text
                
                parseo_fecha = str(year) + "-" + MONTHS[mes.split("-")[0]]+ "-" + fecha_comienzo + " " + str(actual_date.hour) + \
                ":" + str(actual_date.minute) + ":"+ str(actual_date.second)
                #Pasamos la fecha a datetime
                fecha = datetime.datetime.strptime(parseo_fecha,"%Y-%m-%d %H:%M:%S")
                lugar = event.find('div',class_ = "event-place d-block").text
                titulo = event.find('div',class_ = "event-title f1--xxs").text
                img_circuito = event.find('div',class_ = 'event-image').find('img')['data-src']
                #new_races.append()
                writer.writerow((str(year),ronda,fecha,fecha_comienzo,fecha_fin,mes,titulo,lugar,img_circuito))
            f.close()
    else:
         
        upcoming_races = next_races.filter( ( next_races.fecha >= actual_date) ).collect()
        if (len(upcoming_races) == 0):
            
            data = next_races.filter(next_races.temporada == year).first()
            return (data.temporada,data.ronda,data.dia_comienzo,data.dia_final,data.mes,data.nombre,data.pais,data.imagen)
        
        else:
            for e in upcoming_races:
                mes = e.mes.split('-')[0]
                if (int(MONTHS[mes]) >= month):
                    if ( datetime.datetime.strptime(e.fecha,"%Y-%m-%d %H:%M:%S") - actual_date <= datetime.timedelta(14)):
                        return (e.temporada,e.ronda,e.dia_comienzo,e.dia_final,e.mes,e.nombre,e.pais,e.imagen)