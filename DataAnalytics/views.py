from django.shortcuts import render
from .models import Circuito
from .spark_loader import populate
from django.conf import settings


# Create your views here.

''' Vista de la página principal'''
def index(request):
    return render(request, 'index.html',{'STATIC_URL':settings.STATIC_URL})


def load_data(request):
    '''Llamada a la función de carga de datos'''
    c = populate()
    mensaje = 'Se han cargado: ' + str(c) + ' circuitos'
    return render(request,'mensaje.html',{'titulo':'FIN DE CARGA DE LA BD','mensaje':mensaje,'STATIC_URL':settings.STATIC_URL})

'''
def get_list(request):
    print(spark)
    df4 = spark.read.options(delimiter=";", header=True).csv(path)
    df4.show()
    return render(request, 'circuits.html')
'''