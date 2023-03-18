from bs4 import BeautifulSoup
import urllib.request, urllib.parse, urllib.error
import datetime
from pyspark import SparkContext
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
import csv
import re
from .spark_queries import get_constructor_bynameornacionality
import requests

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

''' Función que devuelve una lista con los nombres y apellidos de los pilotos actuales'''
def drivers_scrapping():
    drivers = []
    f = urllib.request.urlopen(URL_F1_OFFICIAL + 'en/drivers.html')
    
    soup = BeautifulSoup(f,"html.parser")
    ''' div que contiene los nombres de los pilotos'''
    data = soup.find_all('div', class_ = "col-xs-8 listing-item--name f1-uppercase")
    for e in data:
        surname = e.find('span', class_="d-block f1-bold--s f1-color--carbonBlack").text
        name = e.find('span', class_="d-block f1--xxs f1-color--carbonBlack").text
        drivers.append((name,surname))
    if len(drivers) < 20:
        other_data = soup.find_all('div', class_ = "col-xs-8 listing-item--name f1-uppercase driver-lastname-primary")
        for e in other_data:
            surname = e.find('span', class_="d-block f1-bold--s f1-color--carbonBlack").text
            name = e.find('span', class_="d-block f1--xxs f1-color--carbonBlack").text
            drivers.append((name,surname))
    return drivers

''' Función que devuelve una lista con los nombres de los equipos actuales'''
def constructors_scrapping():
    constructors = []
    f = urllib.request.urlopen(URL_F1_OFFICIAL+'en/teams.html')
    
    soup = BeautifulSoup(f,"html.parser")
    ''' div que contiene los nombres de los equipos'''
    data = soup.find_all('div', class_ = "name f1-bold--m")
    for row in data:
        data_constructors = row.find('span', class_ = "f1-color--black").text
        constructors.append(data_constructors)
    return constructors


def get_actual_team_byname(name):
    f = urllib.request.urlopen(URL_F1_OFFICIAL+'en/teams.html')
    soup = BeautifulSoup(f,"html.parser")
    teams = soup.find_all('fieldset',class_='listing-item-wrapper')
    for team in teams:
        team_name = team.find('span',class_='f1-color--black').text
        drivers = team.find_all('span',class_='last-name f1-uppercase f1-bold--xs d-block d-lg-inline')
        for driver in drivers:
            if (name == driver.text):
                
                return team_name
                

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


def post_data_driver(url,last_id,surname,name):
    row = []
    with open("./datasets/drivers.csv", "a",newline='') as f:
            writer = csv.writer(f)
            f = urllib.request.urlopen(url)
            soup = BeautifulSoup(f,"html.parser")    
            data = soup.find_all('td', class_ = "stat-value")
            numero = soup.find('div', class_ = "driver-number").find('span').text
            
            for d in data:
                row.append(d.text)
            fecha =  row[-2].split('/')
            month = fecha[1]
            day = fecha[0]
            year = fecha[2]
            fecha = year + "-" + month + "-" + day
            row = [(last_id+1,surname,numero,surname[:3].upper(),name,surname,fecha,row[1],"\\N")]
            writer.writerows(row)    

def get_teams(string):
    temporadas = string.split(' ')[1].split('-')
    if (len(temporadas) == 2):
        a2 = temporadas[1]
    else:
        a2 = None
    a1 = temporadas[0]
    if ( '(' in string and ')' in string):
            dato = string.replace('(','').replace(')','').split(' ')
            string_sin_numeros = re.sub(r'\d+', '', dato[0])
            escuderia = string_sin_numeros.replace('.','')
            ''' Comprobamos definitivamente que la escudería es válida'''
            res = get_constructor_bynameornacionality(escuderia)
            if (len(res) == 0):
                escuderia = None
            else:
                escuderia = res[0]
    else:
        escuderia = None

    return escuderia,a1,a2


''' Se obtiene la clasificación de la carrera a través de la web
    year -> año de la carrera
    location -> lugar donde se disputa'''
def get_data_race(year,location,nombre_carrera):

    # Primero se debe obtener el data-value (valor que se usará) 
    # para construir la url

    values = []

    f = urllib.request.urlopen('https://www.formula1.com/en/results.html/'+str(year)+'/races.html')
    soup = BeautifulSoup(f,'html.parser')

    

    data_values = soup.find_all("a", class_="resultsarchive-filter-item-link FilterTrigger")
    
    for data in data_values:
        if '/' in data['data-value']:
            values.append(data['data-value'])
    
    #Según la localización sabemos qué data-value es el correspondiente

    for v in values:
        
        ''''''
        if (location.lower() == 'united states'):
            if (( ('MIAMI' in nombre_carrera) and ('Miami' in v.split('/')[1]))
                    or ( ('LAS VEGAS' in nombre_carrera) and ('las vegas' in v.split('/')[1].replace('-',' ')))
                    or ( ('united states' in v.split('/')[1].replace('-',' ')))):
                
                suburl = v
                break

        elif (location.lower() == 'italy'):
            if (( ('EMILIA-ROMAGNA'in nombre_carrera) and ('1209' in v.split('/')[0]))
                or ( ('ITALIA' in nombre_carrera) and ('1218' in v.split('/')[0]))):
                
                suburl = v
                break

        elif (location.lower() == v.split('/')[1].replace('-',' ').lower()):
            suburl = v
            break

    #Ya podemos obtener la url de la vista donde se obtiene la clasificación
            
    url = 'https://www.formula1.com/en/results.html/'+str(year)+'/races/'+suburl+"/race-result.html"
    url_speeds = 'https://www.formula1.com/en/results.html/'+str(year)+'/races/'+suburl+"/fastest-laps.html"
    data = get_positions(url)
    speeds = get_speeds(url_speeds)

    return data, speeds


''' Función auxiliar que devuelve la clasificación de la carrera'''
def get_positions(url):

    fres = urllib.request.urlopen(url)
    
    soupres = BeautifulSoup(fres,'html.parser')

    rows = soupres.find_all("tr")
    res = []
    for row in rows:
        subres = []
        cols = row.find_all("td")
        for ele in cols:
            subres.append(ele.text.strip().split("\n"))
        
        res.append(subres)
        
    # Se elimina la primera fila que es vacía
    #Devuelve una lista de listas de listas
    return res[1:]

def get_speeds(url):
    
    fres = urllib.request.urlopen(url)
    soupres = BeautifulSoup(fres,'html.parser')

    rows = soupres.find_all("tr")
    res = []
    for row in rows:
        subres = []
        cols = row.find_all("td")
        for ele in cols:
            subres.append(ele.text.strip().split("\n"))
        
        res.append(subres)
        
    # Se elimina la primera fila que es vacía
    #Devuelve una lista de listas de listas
    return res[1:]


''' Función que devuelve la clasificación de los pilotos en la temporada actual'''

#region Clasificación de los pilotos

def get_standings():

    ''' OBTIENE LA CLASIFICACIÓN DE LOS PILOTOS EN LA TEMPORADA ACTUAL
    Devuelve:
        - Una lista de listas con todos los datos la siguiente estructura:
            [ [posición, piloto, puntos],
        - Una lista de listas con los nombres la siguiente estructura:
            [ [nombre, apellido, abreviatura,
        - Una lista de puntos de cada piloto
    
    '''

    actual_year = datetime.datetime.now().year
    url = "https://www.formula1.com/en/results.html/"+str(actual_year)+"/drivers.html"

    #Obtenemos los datos de la web
    f = urllib.request.urlopen(url)
    
    soup = BeautifulSoup(f,"html.parser")
    data = soup.find('table', class_ = "resultsarchive-table").find_all('tr')
    points = []
    names = []
    res = []
    #Recorrido por filas
    for row in data:
        specific_data = row.find_all('td')
        aux_data = []
        complete_name = []
        if (len(specific_data) != 0):
            points.append(specific_data[-2].text)
        #Recorrido por columnas
        for d in specific_data:
            
            aux = d.find_all('span')
            if (len(aux) == 0):
                aux_data.append(d.text)
            else:
                for a in aux:
                    aux_data.append(a.text)
                    complete_name.append(a.text)
        res.append(aux_data)
        names.append(complete_name)

    #Se elimina la primera fila que es vacía
    return res[1:],names[1:],points

#endregion

#region Clasificación de los equipos
def get_standings_teams():
    actual_year = datetime.datetime.now().year
    url = "https://www.formula1.com/en/results.html/"+str(actual_year)+"/team.html"

    #Obtenemos los datos de la web
    f = urllib.request.urlopen(url)
    
    soup = BeautifulSoup(f,"html.parser")
    data = soup.find('table', class_ = "resultsarchive-table").find_all('tr')

    points = []
    names = []
    res = []
    #Recorrido por filas
    for row in data:
        specific_data = row.find_all('td')
        aux_data = []
        complete_name = []
        if (len(specific_data) != 0):
            points.append(specific_data[-2].text.replace('\n',''))
        #Recorrido por columnas
        for d in specific_data:
            
            aux = d.find_all('span')
            if (len(aux) == 0):
                aux_data.append(d.text)
                complete_name.append(d.text.replace('\n',''))
            else:
                for a in aux:
                    aux_data.append(a.text.replace('\n',''))
                    complete_name.append(a.text.replace('\n',''))
        res.append(aux_data)
        names.append(complete_name)

    #Se elimina la primera fila que es vacía
    
    return res[1:],names[1:],points

#endregion