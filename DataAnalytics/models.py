from django.db import models

# Create your models here.

# RI1: The system shall allow store the data of F1 pilots
class Piloto(models.Model):
    id = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=100)
    apellidos = models.TextField(max_length=100)
    fecha_nacimiento = models.DateTimeField()
    nacionalidad = models.CharField(max_length=100)
    abreviatura = models.TextField(max_length=100)
    #CharField(max_length=100)
    enlace = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre


# RI2: The system shall allow store the data of F1 constrctors
class Constructor(models.Model):
    id = models.IntegerField(primary_key=True)
    referencia = models.CharField(null = True, max_length = 50)
    nombre = models.CharField(max_length=100)
    nacionalidad = models.CharField(max_length=100)
    enlace = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre


# RI3: The system shall allow store the data of F1 circuits
class Circuito(models.Model):
    id = models.IntegerField(primary_key=True)
    nombre_referencia = models.CharField(null = True,max_length=100)
    nombre = models.CharField(max_length=100)
    localizacion = models.CharField(max_length=100)
    pais = models.CharField(max_length=100)
    latitud = models.FloatField()
    altura = models.FloatField(null = True)
    longitud = models.FloatField()
    enlace = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class Carrera(models.Model):
    id = models.IntegerField(primary_key=True)
    temporada = models.BigIntegerField()
    numero = models.BigIntegerField()
    fecha = models.DateTimeField()
    nombre = models.CharField(max_length=100)
    enlace = models.CharField(max_length=100)
    circuito = models.ForeignKey(Circuito, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre

