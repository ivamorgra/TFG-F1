import http.client

conn = http.client.HTTPSConnection("visual-crossing-weather.p.rapidapi.com")

headers = {
    'X-RapidAPI-Key': "16b2332666msh9b5d2d412e7adfcp1004d0jsn01a2fd603c42",
    'X-RapidAPI-Host': "visual-crossing-weather.p.rapidapi.com"
    }

conn.request("GET", "/history?startDateTime=2019-01-01T00%3A00%3A00&aggregateHours=24&location=Washington%2CDC%2CUSA&endDateTime=2019-01-03T00%3A00%3A00&unitGroup=us&dayStartTime=8%3A00%3A00&contentType=csv&dayEndTime=17%3A00%3A00&shortColumnNames=0", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))