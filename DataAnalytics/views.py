from django.shortcuts import render, get_object_or_404, HttpResponse

from DataAnalytics.forms import CircuitoBusquedaForm, ConstructorBusquedaForm, PilotoBusquedaForm
from .models import Circuito, Piloto, Constructor
from .spark_loader import populate,load_df
from django.conf import settings
from .spark_queries import driver_basic_stats,constructor_basic_stats, get_circuit_bynameornacionality, get_constructor_bynameornacionality, get_driver_bynameornacionality
from .twitter import get_actual_followers
# Create your views here.

''' Vista de la página principal'''
def index(request):
    return render(request, 'index.html',{'STATIC_URL':settings.STATIC_URL})


def load_data(request):
    '''Llamada a la función de carga de datos'''
    c,d,co = populate()
    mensaje = 'La carga se ha realizado con éxito. Se han cargado: ' + str(c) + ' circuitos, '+ str(d) + ' pilotos y '+ str(co)+ ' constructores.'
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
   
    return render(request,'driver.html',{'driver':driver,'stats':stats,'STATIC_URL':settings.STATIC_URL})

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


#API TWITTER    

def get_twitter_stats(request):
    followers_stats = get_actual_followers()
    return render(request,'twitter_api/example.html',{'followers_stats':followers_stats,'STATIC_URL':settings.STATIC_URL})