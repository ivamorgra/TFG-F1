# wheaterAPI.com
#Visual Crossing API

import requests
import json


def get_weather(location, date, end_date,start_time,end_time):
    meteo = []
    url = "https://visual-crossing-weather.p.rapidapi.com/history"
    key = '\'' + location + '\''
    querystring = {"startDateTime":date,\
        "aggregateHours":"24","location":location,\
            "endDateTime":end_date,\
                "unitGroup":"us","dayStartTime":start_time,\
                    "contentType":"json","dayEndTime":end_time,\
                        "shortColumnNames":"0"}

    headers = {
        "X-RapidAPI-Key": "16b2332666msh9b5d2d412e7adfcp1004d0jsn01a2fd603c42",
        "X-RapidAPI-Host": "visual-crossing-weather.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)
    if response.status_code == 200:
    # Cargue los datos devueltos en un objeto de Python
        
        lista_valores = list(response.json().values())
        data_dict = lista_valores[-1]
        data_parsed = list(data_dict.values())[0]['values'][0]
        temperatura = data_parsed['temp']
        
        precipitacion = data_parsed['precip']
        humedad = data_parsed['humidity']
        condiciones = data_parsed['conditions']
        min_temp = data_parsed['mint']
        meteo.append((min_temp,temperatura,precipitacion,humedad,condiciones))
        return meteo
    else:
    # Mostrar un error en caso de que la solicitud haya fallado
        print("Error:", response.status_code)
    #print(response.text)

    