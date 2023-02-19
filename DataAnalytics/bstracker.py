from bs4 import BeautifulSoup
import urllib.request, urllib.parse, urllib.error

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


        