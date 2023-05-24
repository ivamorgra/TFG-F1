from django.test import TestCase
from requests import patch
from DataAnalytics.models import Carrera, Circuito
from DataAnalytics.spark_loader import load_drivers
from DataAnalytics.views import list_drivers
from DataAnalytics.forms import PilotoBusquedaForm
from unittest.mock import Mock

class RaceTest(TestCase):
    def setUp(self):
        self.circuit1 = Circuito.objects.create(
            id = 1,
            nombre = 'Circuit1',
            localizacion = 'Spain',
            pais = 'Spain',
            longitud = 1.0,
            altura = 1.0,
            latitud = 1.0,
            enlace = 'https://www.circuit1.com/',
        )  

        self.race = Carrera.objects.create(
            id = 1,
            nombre = 'Race1',
            fecha = '2020-01-01',
            enlace = 'https://www.race1.com/',
            temporada = 2020,
            numero = 1,
            circuito = self.circuit1,
        )
        self.mocker = Mock()

    def test_get_circuit_name_by_race(self):
        race = Carrera.objects.get(id=1)
        circuit = race.circuito
        self.assertEqual(circuit.nombre, 'Circuit1')

    def test_get_race(self):
        race = Carrera.objects.get(id=1)
        self.assertEqual(race.nombre, 'Race1')
    
    def test_update_race(self):
        race = Carrera.objects.get(id=1)
        race.nombre = 'Race2'
        race.fecha = '2020-01-02'
        race.enlace = 'https://www.race2.com/'
        race.numero = 2
        race.save()
        self.assertEquals(race.nombre, 'Race2')
        self.assertEquals(race.fecha, '2020-01-02')
        self.assertEquals(race.enlace, 'https://www.race2.com/')
        self.assertEquals(race.numero, 2)
    
    def test_delete_race(self):
        race = Carrera.objects.get(id=1)
        race.delete()
        self.assertEqual(Carrera.objects.all().count(), 0)
        self.assertEqual(Circuito.objects.all().count(), 1)
    
