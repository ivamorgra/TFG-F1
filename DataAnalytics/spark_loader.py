from django.db.models import Q
from .models import Circuito, Piloto, Constructor, Carrera, Periodo
from pyspark import SparkContext
from pyspark.sql import SparkSession
import datetime
from .spark_queries import is_active_driver
from .bstracker import drivers_scrapping,constructors_scrapping,get_actual_team_byname,post_data_driver,get_data_race,next_race_scrapping
from pyspark.sql.functions import col
import threading
import time
import csv


spark = SparkSession.Builder().appName("F1Analytics").getOrCreate()

URL = 'https://www.formula1.com/'

def populate():
    c=load_circuits()
    co = load_constructors()
    p = load_drivers()
    pe = load_periods()
    r = load_races()
    
    return (c,p,co,r)



def load_circuits():
    ''' Borrado de los datos de la tabla por si ya estaban cargados de antes'''
    Circuito.objects.all().delete()

    '''Creación de lista de objetos de tipo Circuito'''
    circuits = []
    '''Carga de los datos de los circuitos'''
    df = spark.read.csv("./datasets/circuits.csv", header=True,sep=",")
    for row in df.collect():

        if row[7] == '\\N':
            circuit = Circuito(
            id = row[0],
            nombre_referencia = row[1],
            nombre = row[2],
            localizacion = row[3],
            pais = row[4],
            latitud = row[5],
            longitud = row[6],
            altura = None,
            enlace = row[8]
            )
        else:

            circuit = Circuito(
                id = row[0],
                nombre_referencia = row[1],
                nombre = row[2],
                localizacion = row[3],
                pais = row[4],
                latitud = row[5],
                longitud = row[6],
                altura = row[7],
                enlace = row[8]
            )
            
        circuits.append(circuit)
    
    Circuito.objects.bulk_create(circuits)
    return Circuito.objects.count()

def load_drivers():
    Piloto.objects.all().delete()
    actual_drivers = drivers_scrapping()
    
    '''Creación de lista de objetos de tipo Piloto'''
    drivers = []
    
    #Antes de cargar los datos de los pilotos, nos aseguramos de que estén todos los pilotos en el registro
    check_drivers(actual_drivers)

    '''Carga de los datos de los circuitos'''
    df = spark.read.csv("./datasets/drivers.csv", header=True,sep=",")


    for row in df.collect():
        is_active = is_active_driver(actual_drivers,row.forename,row.surname)
        
        driver = Piloto(
            id = row[0],
            nombre = row[4],
            apellidos = row[5],
            fecha_nacimiento = row[6],
            nacionalidad = row[7],
            abreviatura = row[3],
            enlace = row[8],
            activo = is_active
        )
        drivers.append(driver)
    
    Piloto.objects.bulk_create(drivers)
    return Piloto.objects.count()

def load_constructors():
    Constructor.objects.all().delete()
    actual_teams = constructors_scrapping()
    '''Creación de lista de objetos de tipo Piloto'''
    constructors = []
    '''Carga de los datos de los circuitos'''
    df = spark.read.csv("./datasets/constructors.csv", header=True,sep=",")
    for row in df.collect():
        nombre = row.name
        is_active = True
        if (len(list(filter(lambda x: nombre in x, actual_teams))) == 0):
            is_active = False
        if (row[2] == 'Alpine F1 Team'):
            is_active = True
        constructor = Constructor(
            id = row[0],
            referencia = row[1],
            nombre = row[2],
            nacionalidad = row[3],
            enlace = row[4],
            activo = is_active
        )
        constructors.append(constructor)
    
    Constructor.objects.bulk_create(constructors)
    return Constructor.objects.count()


def load_races():
    ''' Borrado de los datos de la tabla por si ya estaban cargados de antes'''
    Carrera.objects.all().delete()

    '''Creación de lista de objetos de tipo Carrera'''
    races = []
    '''Carga de los datos de los carreras'''
    df = spark.read.csv("./datasets/races.csv", header=True,sep=",")
    for row in df.collect():
        
        if (int(row[1]) > 2020 ):
            fecha = row[5].split("/")
            date_time_str = row[1] + "-" + fecha[1] + "-" + fecha[0] + ' ' + row[6]
            date_time_obj = datetime.datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')
            race = Carrera(
                id = row[0],
                temporada = row[1],
                numero = row[2],
                nombre = row[4],
                fecha = date_time_obj,
                enlace = row[-1],
                circuito = Circuito.objects.get(id = row[3])
            )
            races.append(race)
    
    Carrera.objects.bulk_create(races)
    return Carrera.objects.count()


def load_periods():
    Periodo.objects.all().delete()
    fecha_actual = datetime.datetime.now()
    temporada_actual = int(fecha_actual.year)
    pilotos = Piloto.objects.all()
    teams = spark.read.csv("./datasets/constructors.csv", header=True,sep=",")
    periods = []

    for piloto in pilotos:
        
        if (piloto.activo == True):
            list_actual_team_name = []
            ''' Si el piloto está activo, añadimos el periodo actual'''
            actual_team_name = get_actual_team_byname(piloto.apellidos)
                
            if (actual_team_name == "Red Bull Racing"):
                actual_team_name = "Red Bull"
            elif (actual_team_name == "Alpine"):
                actual_team_name = "Alpine F1 Team"

            list_actual_team_name.append(actual_team_name)
            
            query_name = teams.filter( (teams.name.isin(list_actual_team_name)) | teams.constructorRef.isin(list_actual_team_name) )
            
            period = Periodo(
                temporada_inicio = temporada_actual,
                temporada_fin = temporada_actual,
                constructor = Constructor.objects.get(nombre = query_name.collect()[0].name),
                piloto = piloto
            )
            
            periods.append(period) 
        
    Periodo.objects.bulk_create(periods)
    return Periodo.objects.count()


def check_drivers(actual_drivers):
    
    reg_drivers = spark.read.csv("./datasets/drivers.csv", header=True,sep=",")
    for driver in actual_drivers:
        if (len(reg_drivers.filter((reg_drivers.forename == driver[0]) & (reg_drivers.surname == driver[1])).collect()) == 0):
            #Para saber el último id
            reg_drivers = spark.read.csv("./datasets/drivers.csv", header=True,sep=",")
            total = reg_drivers.count()
            #Si contiene espacios en blanco, los sustituimos por guiones
            if (' ' in driver[0] or ' ' in driver[1]):
                nombre = driver[0].replace(" ","-")
                apellido = driver[1].replace(" ","-")
                url = "https://www.formula1.com/en/drivers/" + nombre.lower() + "-" + apellido.lower() + ".html"
            else:

                url = "https://www.formula1.com/en/drivers/" + driver[0].lower() + "-" + driver[1].lower() + ".html"
            
            # Actualiza el registro con los datos del nuevo piloto
            post_data_driver(url,total+1,driver[1],driver[0])
    return False




def load_df():
    cons_res = spark.read.csv("./datasets/constructor_results.csv", header=True,sep=",")
    races = spark.read.csv("./datasets/races.csv", header=True,sep=",")
    seasons =  spark.read.csv("./datasets/seasons.csv", header=True,sep=",")
    results = spark.read.csv("./datasets/results.csv", header=True,sep=",")
    sresults = spark.read.csv("./datasets/sprint_results.csv", header=True,sep=",")
    status =  spark.read.csv("./datasets/status.csv", header=True,sep=",")
    const_clas = spark.read.csv("./datasets/constructor_standings.csv", header=True,sep=",")
    laps =  spark.read.csv("./datasets/lap_times.csv", header=True,sep=",")
    stops =  spark.read.csv("./datasets/pit_stops.csv", header=True,sep=",")
    qualy_results =  spark.read.csv("./datasets/qualifying.csv", header=True,sep=",")

    return cons_res.count(),races.count(),seasons.count(),results.count(),sresults.count(),status.count(),const_clas.count(),laps.count(),stops.count(),qualy_results.count()


### AUTOMATIZACIÓN DE LA CARGA DE DATOS DE CARRERAS ###

''' Con esta función se comprueba si ya ha pasado una carrera y se actualiza el dataset y la BD de carreras'''
def check_date():
    #Se accede a la última fila del dataset para obtener la fecha de la última actualización y evitar una sobrecarga en la API
    actual_date = datetime.datetime.now()
    df = spark.read.csv("./datasets/next_races.csv", header=True)
    
    races = df.collect()
    res = False
    for row in races:
        fecha = row['fecha'] 
        fecha = datetime.datetime.strptime(fecha, '%Y-%m-%d %H:%M:%S')
        periodo = actual_date - fecha
        if (periodo >= datetime.timedelta(days=1)) & (periodo <= datetime.timedelta(days=5)):
            #Si está dentro de ese período, entonces mira si ya se ha actualizado el dataset
            #Se busca en la última fila del dataset
            races = spark.read.csv("./datasets/results.csv",header=True)
            total = races.count()
            
            last_race = races.filter(races.resultId == total).collect()[0]
            
            last_race_id = last_race["raceId"]
            
            race_bd = Carrera.objects.get(id = last_race_id)
            registered_day = race_bd.fecha.day
            registered_month = race_bd.fecha.month
            registered_year = race_bd.fecha.year
            
            # Se suman 2 días ya que el día de la fecha es anterior a la carrera 
            day = int(row['dia_comienzo'])
            month = fecha.month
            year = fecha.year

            if ((day == registered_day) & (month == registered_month)
                & (year == registered_year)):
                res = False
                break
            else:
                res = True
                break
    return res

def post_speeds(race_id,speeds):

    #Obtenemos el número de líneas del dataset

    with open("./datasets/aux_results.csv", 'r') as archivo:
        reader = csv.reader(archivo)
        lista = list(reader)
    archivo.close()

    
    with open("./datasets/results.csv", 'a',newline="") as f:
        for row in lista:

            for speed in speeds:
                numero = speed[2][0]

                if ( row[4] == numero  and int(row[1]) == race_id):

                    # fastestLap
                    lap = speed[5][0]

                    #fastestLapTime
                    flap = speed[7][0]
                    #fastestLapSpeed
                    flaps = speed[8][0]

                    #rank
                    rank = speed[1][0]
                    new_row = [row[0],row[1],row[2],row[3],row[4],
                               row[5],row[6],row[7],row[8],row[9],
                               row[10],row[11],row[12],lap,rank,flap,flaps,row[-1]]
                    
                    writer = csv.writer(f)
                    writer.writerow(new_row)
    
    f.close()

    #Borrado de las filas del dataset auxiliar

    with open("./datasets/aux_results.csv",'w',newline="") as aux:
        writer = csv.writer(aux)
        writer.writerows([])
    
    
''' En esta función con los datos devueltos se actualiza el dataset 
 de los resultados de las carreras'''
def write_results_csv(year,location,nombre_carrera,ronda): 

    data,speeds = get_data_race(year,location,nombre_carrera)
    results = spark.read.csv("./datasets/results.csv", header=True,sep=",")
    total = results.count()

    # Obtener el id de la carrera
    carrera = Carrera.objects.get(temporada = year,numero = ronda )
    carrera_id = carrera.id
    with open('./datasets/aux_results.csv', 'a',newline="") as f:
                
                for row in data:
                    result_id = total +1

                    if (row[3][0] == 'Zhou'):
                        conductor = Piloto.objects.filter(Q(apellidos__icontains= row[3][0]), activo = 1).get()
                        conductor_id = conductor.id
                    else:
                        conductor = Piloto.objects.filter(Q(nombre__icontains= row[3][0]), activo = 1).get()
                        conductor_id = conductor.id
                    
                    nombre = row[4][0].split(" ")[0]
                    
                    constructor = Constructor.objects.filter(Q(nombre__icontains=nombre),activo = 1).get()
                    constructor_id = constructor.id
    
                    laps = row[5][0]
                    
                    points = row[7][0]
                     
                    if ('lap' in row[6][0] or 'laps' in row[6][0]):
                        time = "\\N"
                        position = 0
                    elif (row[6][0] == 'DNF'):
                        time = "\\N"
                        status_id = 3
                    else:
                        position = int(row[1][0])
                        time = row[6][0]
                        status_id = 1
                    
                    number = row[2][0]

                    grid = "\\N"
                    position_text = "\'"+str(position)+"\'"
                    position_order = "\\N"
                    milliseconds = "\\N"
                    fastest_lap = ""
                    rank = ""
                    fastest_lap_time = ""
                    fastest_lap_speed = ""

                    fila = [result_id,carrera_id,conductor_id,constructor_id,number,
                             grid,position,position_text,position_order,points,
                             laps,time,milliseconds,fastest_lap,rank,fastest_lap_time,
                             fastest_lap_speed,status_id]
                    writer = csv.writer(f)
                    writer.writerow(fila)
        
                    total += 1
                
                f.close()
    
    post_speeds(carrera_id,speeds)
            




class AutoThread(threading.Thread):
    def __init__(self, flag, *args, **kwargs):
        self.flag = flag
        super().__init__(*args, **kwargs)

    def run(self):

        print("Executing Daemon Auto Race Thread: " + self.name)
       
        # Se comprueba la última actualización
        if check_date():
            print("Updating data...")
            #Actualización del registro (dataset)
            carrera = next_race_scrapping()
            
            year = carrera[0]
            round = int(carrera[1].split(" ")[1])
            race = Carrera.objects.get(numero = (round -1), temporada = year)
            localizacion = race.circuito.pais
            nombre = race.nombre
            write_results_csv(year,localizacion,nombre,round-1)
            
        else:
            print("Data races already updated :)")
        time.sleep(60*60*24)

flag = True
my_thread = AutoThread(flag)
my_thread.start()