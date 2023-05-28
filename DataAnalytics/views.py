from django.shortcuts import render, get_object_or_404, HttpResponse
from django.core.paginator import Paginator
from DataAnalytics.forms import CircuitoBusquedaForm, ConstructorBusquedaForm, PilotoBusquedaForm, CarreraBusquedaForm
from .models import Circuito, Piloto, Constructor, Periodo
from .spark_loader import populate,load_df
from django.conf import settings
from .spark_queries import *
from .spark_queries_teams import *
from .auto_races import get_race
from .meteo import get_weather
from .bstracker import next_race_scrapping
from .trends import search_trends
import matplotlib.pyplot as plt
import json

# Create your views here.

''' Vista de la página principal'''
def index(request):
    next_race = next_race_scrapping()
    #fig = search_trends(request)
    
    
    return render(request, 'menu.html',{'race':next_race,'STATIC_URL':settings.STATIC_URL})


def load_data(request):
    '''Llamada a la función de carga de datos'''
    c,d,co,r = populate()
    mensaje = 'La carga se ha realizado con éxito. Se han cargado: ' + str(c) + ' circuitos, '+ str(d) + ' pilotos, '+ str(co)+ ' constructores y '+ str(r)+ ' carreras.'
    return render(request,'mensaje.html',{'titulo':'FIN DE CARGA DE LA BASE DE DATOS','mensaje':mensaje,'STATIC_URL':settings.STATIC_URL})

def load_dataframes(request):
    (cr,r,s,re,sre,st,cc,l,sto,q) = load_df()
    mensaje = 'La carga de los datos se ha realizado con éxito. Se han cargado: \n   ' \
          + ' {} resultados de constructores. \n'.format(cr) \
          + ' {} carreras. \n'.format(r) \
          + '{} temporadas. \n'.format(s) \
          + '{} resultados de carreras. \n'.format(re) \
          + '{} resultados de carreras al sprint. \n'.format(sre) \
          + '{} estados de pilotos y coches en carreras. \n '.format(st) \
          + '{} clasificaciones de los constructores al finalizar cada carrera. \n'.format(cc) \
          + '{} tiempos de vueltas. \n'.format(l) \
          + '{} tiempos en las paradas. \n'.format(sto) \
          + '{} tiempos de clasificación en las diferentes sesiones de clasificación.'.format(q)


    return render(request,'mensaje.html',{'titulo':'FIN DE CARGA DE LOS DATOS','mensaje':mensaje,'STATIC_URL':settings.STATIC_URL})


def list_drivers(request):
   
    drivers = Piloto.objects.all().order_by('-activo')

    search = False
    formulario = PilotoBusquedaForm()

    if request.method=='POST':
        formulario = PilotoBusquedaForm(request.POST)
        
        if formulario.is_valid():
            value=formulario.cleaned_data['input']
            drivers = get_driver_bynameornacionality(value)
            search = True
   
    paginator = Paginator(drivers, 10)
    page = request.GET.get('page')
    drivers_page = paginator.get_page(page)
    num_pages = paginator.num_pages
    next_pages = []

    if int(page) + 1 <= num_pages:
        next_pages.append(int(page) + 1)
    if int(page) + 2 <= num_pages:
        next_pages.append(int(page) + 2)
    
    return render(request,'drivers/list.html',{'page_obj': drivers_page,'pages':next_pages,'search':search,'formulario':formulario,'drivers':drivers,'STATIC_URL':settings.STATIC_URL})


def get_driver(request,id):
    '''Llamada a la función de carga de datos'''
    driver = get_object_or_404(Piloto,pk=id)
    stats = driver_basic_stats(id)
    season = datetime.datetime.now().year
    periodo = Periodo.objects.get(piloto=driver)
    if (periodo is not None):
        constructor = periodo.constructor
    
    if(driver.activo == 1):
        avg_punt = get_driver_avg_points_by_season(driver.id,season)
        tot_punt = get_driver_total_points_by_season(driver.id,season)
        max_pos = get_driver_max_position_by_season(driver.id,season)
        min_pos = get_driver_min_position_by_season(driver.id,season)
        wins = get_driver_wins_by_season(driver.id,season)
    x,y,media,total,paises_tendencia,paises_tendencia_values = search_trends(driver.nombre,150)

    paises,numero = get_country_races_by_driver(id)
    
    meses = json.dumps(x)
    valores = json.dumps(y)
    
    paises_tendencia = json.dumps(paises_tendencia)

    context = {'paises':paises,
               'valores':numero,
               'total':total,
               'media':media,
               'paises_tendencia':paises_tendencia,
               'valores_paises':paises_tendencia_values,
               'x':meses,'y':valores,'driver':driver,'stats':stats,
                'constructor':constructor,'avg_punt':avg_punt,'tot_punt':tot_punt,
                'max_pos':max_pos,'min_pos':min_pos,'wins':wins,
               'STATIC_URL':settings.STATIC_URL}
    
    return render(request,'drivers/profile.html',context)
    
def get_constructors(request):
    constructors = Constructor.objects.all().order_by('-activo')
    formulario = ConstructorBusquedaForm()
    search = False
    if request.method=='POST':
        formulario = ConstructorBusquedaForm(request.POST)
        
        if formulario.is_valid():
            value=formulario.cleaned_data['input']
            constructors = get_constructor_bynameornacionality(value)
            search = True

    paginator = Paginator(constructors, 10)
    page = request.GET.get('page')
    ctos_page = paginator.get_page(page)
    num_pages = paginator.num_pages
    next_pages = []

    if int(page) + 1 <= num_pages:
        next_pages.append(int(page) + 1)
    if int(page) + 2 <= num_pages:
        next_pages.append(int(page) + 2)

    return render(request,'teams/list.html',{'page_obj': ctos_page,'pages':next_pages,'search':search,'formulario':formulario,'constructors':constructors,'STATIC_URL':settings.STATIC_URL})


def get_constructor(request,id):
    '''Llamada a la función de carga de datos'''
    constructor = get_object_or_404(Constructor,pk=id)
    season = datetime.datetime.now().year

    per = Periodo.objects.filter(constructor=constructor).order_by('-piloto_id')
    pilotos = []
    pilotos_apellidos = []
    for p in per:
        pilotos.append(p.piloto.nombre)
        pilotos_apellidos.append(p.piloto.apellidos)
    stats = constructor_basic_stats(id)
    max_pos = get_team_max_position_by_season(id,season)
    min_pos = get_team_min_position_by_season(id,season)
    tot_punt = get_team_total_points_by_season(id,season)
    wins = get_team_wins_by_season(id,season)

    context = {'stats':stats,
               'constructor':constructor,
                'max_pos':max_pos,
                'min_pos':min_pos,
                'pilotos':pilotos,
                'pilotos_apellidos':pilotos_apellidos,
                'tot_punt':tot_punt,
                'wins':wins,
               'STATIC_URL':settings.STATIC_URL}
    
    return render(request,'teams/profile.html',context)

def list_circuits(request):
    circuits =  Circuito.objects.all().order_by('-nombre')
    formulario = CircuitoBusquedaForm()
    search = False
    if request.method=='POST':
        formulario = CircuitoBusquedaForm(request.POST)
        
        if formulario.is_valid():
            value=formulario.cleaned_data['input']
            circuits = get_circuit_bynameornacionality(value)
            search = True
    
    paginator = Paginator(circuits, 10)
    page = request.GET.get('page')
    cts_page = paginator.get_page(page)
    num_pages = paginator.num_pages
    next_pages = []

    if int(page) + 1 <= num_pages:
        next_pages.append(int(page) + 1)
    if int(page) + 2 <= num_pages:
        next_pages.append(int(page) + 2)

    
    return render(request,'circuits/list.html',{'page_obj': cts_page,'pages':next_pages,'search':search,'formulario':formulario,'circuits':circuits,'STATIC_URL':settings.STATIC_URL})

def get_circuit(request,id):
    circuit = get_object_or_404(Circuito,pk=id)
    
    return render(request,'circuits/profile.html',{'c':circuit,'STATIC_URL':settings.STATIC_URL})


def list_races(request):
    carreras = Carrera.objects.all().order_by('-fecha')
    formulario = CarreraBusquedaForm()
    search = False
    if request.method=='POST':
        formulario = CarreraBusquedaForm(request.POST)
        
        if formulario.is_valid():
            value=formulario.cleaned_data['input']
            carreras = get_race_bynameorseason(value)
            search = True
    
    paginator = Paginator(carreras, 10)
    page = request.GET.get('page')
    races_page = paginator.get_page(page)
    num_pages = paginator.num_pages
    next_pages = []

    if int(page) + 1 <= num_pages:
        next_pages.append(int(page) + 1)
    if int(page) + 2 <= num_pages:
        next_pages.append(int(page) + 2)

    return render(request,'races/list.html',{'page_obj': races_page,'pages':next_pages,'search':search,'formulario':formulario,'c':carreras,'STATIC_URL':settings.STATIC_URL})

def details_race(request,id):
    bool_meteo = True
    bool_data_fl = True
    bool_data_ms = True

    carrera,circuit,podium,pole,meteo,data_fl,data_ms = get_race(id)
    if (meteo != []):
        if (meteo[0] == 'No hay datos disponibles ya que la carrera se disputó antes del año 2000'):
            bool_meteo = False

        if (data_fl[0] == 'No hay datos disponibles'):
            bool_data_fl = False
        
        if (data_ms[0] == 'No hay datos disponibles'):
            bool_data_ms = False
    else:
        bool_meteo = False
        bool_data_fl = False
        bool_data_ms = False
    
    return render(request,'races/details.html',{'fl':bool_data_fl,'ms':bool_data_ms,'nm':bool_meteo,'v_rapida':data_fl,'max_vel':data_ms,'m':meteo,'pole':pole,'c':carrera,'cir':circuit,'p':podium,'STATIC_URL':settings.STATIC_URL})
