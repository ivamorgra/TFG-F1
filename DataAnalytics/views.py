from django.shortcuts import render, get_object_or_404, HttpResponse

from DataAnalytics.forms import CircuitoBusquedaForm, ConstructorBusquedaForm, PilotoBusquedaForm, CarreraBusquedaForm
from .models import Circuito, Piloto, Constructor
from .spark_loader import populate,load_df
from django.conf import settings
from .spark_queries import *
from .auto_races import get_race
from .meteo import get_weather
from .bstracker import next_race_scrapping
from .trends import search_trends
import matplotlib.pyplot as plt
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
   
    drivers = Piloto.objects.all()
    search = False
    formulario = PilotoBusquedaForm()

    if request.method=='POST':
        formulario = PilotoBusquedaForm(request.POST)
        
        if formulario.is_valid():
            value=formulario.cleaned_data['input']
            drivers = get_driver_bynameornacionality(value)
            search = True

    return render(request,'drivers.html',{'search':search,'formulario':formulario,'drivers':drivers,'STATIC_URL':settings.STATIC_URL})


def get_driver(request,id):
    '''Llamada a la función de carga de datos'''
    driver = get_object_or_404(Piloto,pk=id)
    stats = driver_basic_stats(id)
    
    x,y,media,total = search_trends(driver.nombre,150)
    paises,numero = get_country_races_by_driver(id)

    context = {'paises':paises,
               'valores':numero,
               'total':total,
               'media':media,
               'x':x,'y':y,'driver':driver,'stats':stats,
               'STATIC_URL':settings.STATIC_URL}
    
    return render(request,'drivers/profile.html',context)
    
def get_constructors(request):
    constructors = Constructor.objects.all()
    formulario = ConstructorBusquedaForm()
    search = False
    if request.method=='POST':
        formulario = ConstructorBusquedaForm(request.POST)
        
        if formulario.is_valid():
            value=formulario.cleaned_data['input']
            constructors = get_constructor_bynameornacionality(value)
            search = True

    return render(request,'constructors.html',{'search':search,'formulario':formulario,'constructors':constructors,'STATIC_URL':settings.STATIC_URL})


def get_constructor(request,id):
    '''Llamada a la función de carga de datos'''
    constructor = get_object_or_404(Constructor,pk=id)
    stats = constructor_basic_stats(id)
    return render(request,'constructor.html',{'constructor':constructor,'stats':stats,'STATIC_URL':settings.STATIC_URL})

def list_circuits(request):
    circuits =  Circuito.objects.all()
    formulario = CircuitoBusquedaForm()
    search = False
    if request.method=='POST':
        formulario = CircuitoBusquedaForm(request.POST)
        
        if formulario.is_valid():
            value=formulario.cleaned_data['input']
            circuits = get_circuit_bynameornacionality(value)
            search = True
        
    
    return render(request,'circuits.html',{'search':search,'formulario':formulario,'circuits':circuits,'STATIC_URL':settings.STATIC_URL})

def get_circuit(request,id):
    circuit = get_object_or_404(Circuito,pk=id)
    
    return render(request,'circuit.html',{'c':circuit,'STATIC_URL':settings.STATIC_URL})


def list_races(request):
    carreras = get_races()
    formulario = CarreraBusquedaForm()
    search = False
    if request.method=='POST':
        formulario = CarreraBusquedaForm(request.POST)
        
        if formulario.is_valid():
            value=formulario.cleaned_data['input']
            carreras = get_race_bynameorseason(value)
            search = True
        
    return render(request,'races/list.html',{'search':search,'formulario':formulario,'c':carreras,'STATIC_URL':settings.STATIC_URL})

def details_race(request,id):
    bool_meteo = True
    bool_data_fl = True
    bool_data_ms = True

    carrera,circuit,podium,pole,meteo,data_fl,data_ms = get_race(id)
    print (meteo)
    if (meteo[0] == 'No hay datos disponibles ya que la carrera se disputó antes del año 2000'):
        bool_meteo = False

    if (data_fl[0] == 'No hay datos disponibles'):
        bool_data_fl = False
    
    if (data_ms[0] == 'No hay datos disponibles'):
        bool_data_ms = False

    return render(request,'races/details.html',{'fl':bool_data_fl,'ms':bool_data_ms,'nm':bool_meteo,'v_rapida':data_fl,'max_vel':data_ms,'m':meteo,'pole':pole,'c':carrera,'cir':circuit,'p':podium,'STATIC_URL':settings.STATIC_URL})
