# wheaterAPI.com
#Visual Crossing API

import requests
import json


def get_weather(location, date, end_date,start_time,end_time):
    url = "https://visual-crossing-weather.p.rapidapi.com/history"

    querystring = {"startDateTime":date,\
        "aggregateHours":"24","location":location,\
            "endDateTime":end_date,\
                "unitGroup":"us","dayStartTime":start_time,\
                    "contentType":"csv","dayEndTime":end_time,\
                        "shortColumnNames":"0"}

    headers = {
        "X-RapidAPI-Key": "16b2332666msh9b5d2d412e7adfcp1004d0jsn01a2fd603c42",
        "X-RapidAPI-Host": "visual-crossing-weather.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)
    
    print(response.text)
    return end_time
    