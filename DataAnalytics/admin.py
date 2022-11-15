from django.contrib import admin
from DataAnalytics.models import Piloto,Circuito,Constructor
# Register your models here.

@admin.register(Piloto)
class PilotoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'apellidos', 'fecha_naciomiento', 'nacionalidad', 'abreviatura', 'enlace']

@admin.register(Circuito)
class CircuitoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'localizacion', 'pais', 'latitud', 'longitud', 'enlace']
    
@admin.register(Constructor)
class ConstructorAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'nacionalidad', 'enlace']