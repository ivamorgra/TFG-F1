from django.test import TestCase
from requests import patch
from DataAnalytics.models import Piloto
from DataAnalytics.models import Piloto
from DataAnalytics.spark_loader import load_drivers
from DataAnalytics.views import list_drivers
from DataAnalytics.forms import PilotoBusquedaForm
import unittest
from unittest.mock import Mock


class DriverTest(TestCase):
    def setUp(self):
        self.my_model = Piloto.objects.create(
            id = 1,
            nombre='Driver1',
            apellidos = 'Test',
            fecha_nacimiento = '1990-01-01',
            abreviatura = 'DT',
            activo = 0,
            enlace = "\\N",
            nacionalidad = 'Spanish',
    )
        self.my_model.save()
        self.my_model2 = Piloto.objects.create(
            id = 2,
            nombre='Driver2',
            apellidos = 'Test2',
            fecha_nacimiento = '1990-01-01',
            abreviatura = 'DT',
            activo = 1,
            enlace = "\\N",
            nacionalidad = 'Spanish',
    )
        self.my_model2.save()
        self.mocker = Mock()
        

    def test_active_drivers(self):
        self.assertEqual(Piloto.objects.all().filter(activo=1).count(), 1)
    
    def test_inactive_drivers(self):
        self.assertEqual(Piloto.objects.all().filter(activo=0).count(), 1)
    
    ############# TESTS DE MODELO #############
    # Tests that a Piloto object can be created with all required fields. 
    def test_create_piloto_with_required_fields(self):
        piloto = Piloto.objects.create(
            id=3,
            nombre="Lewis",
            apellidos="Hamilton",
            fecha_nacimiento="1985-01-07 00:00:00",
            nacionalidad="British",
            abreviatura="HAM",
            activo=True,
            enlace="https://www.lewishamilton.com/"
        )
        assert piloto.id == 3
        assert piloto.nombre == "Lewis"
        assert piloto.apellidos == "Hamilton"
        assert piloto.fecha_nacimiento == "1985-01-07 00:00:00"
        assert piloto.nacionalidad == "British"
        assert piloto.abreviatura == "HAM"
        assert piloto.activo == True
        assert piloto.enlace == "https://www.lewishamilton.com/"

    # Tests that the __str__ method returns the name of a Piloto object. 
    def test_retrieve_piloto_name(self):
        piloto = Piloto.objects.create(
            id=4,
            nombre="Lewis",
            apellidos="Hamilton",
            fecha_nacimiento="1985-01-07 00:00:00",
            nacionalidad="British",
            abreviatura="HAM",
            activo=True,
            enlace="https://www.lewishamilton.com/"
        )
        assert str(piloto) == "Lewis"
    
    # Tests that all Piloto objects can be retrieved from the database. 
    def test_retrieve_all_pilotos(self):
        piloto1 = Piloto.objects.create(
            id=7,
            nombre="Lewis",
            apellidos="Hamilton",
            fecha_nacimiento="1985-01-07 00:00:00",
            nacionalidad="British",
            abreviatura="HAM",
            activo=True,
            enlace="https://www.lewishamilton.com/"
        )
        piloto2 = Piloto.objects.create(
            id=8,
            nombre="Max",
            apellidos="Verstappen",
            fecha_nacimiento="1997-09-30 00:00:00",
            nacionalidad="Dutch",
            abreviatura="VER",
            activo=True,
            enlace="https://www.verstappen.nl/"
        )
        pilotos = Piloto.objects.all()
        assert len(pilotos) == 4
        assert piloto1 in pilotos
        assert piloto2 in pilotos
    
    # Tests that a Piloto object cannot be created with a very long name or abreviatura. 
    def test_create_piloto_with_long_name_or_abreviatura(self):
        with self.assertRaises(Exception):
            Piloto.objects.create(
                id=9,
                nombre="Lewis" * 22,
                apellidos="Hamilton",
                fecha_nacimiento="1985-01-07 00:00:00",
                nacionalidad="British",
                abreviatura="HAM" * 20,
                activo=True,
                enlace="https://www.lewishamilton.com/"
            )

    # Tests that the fields of a Piloto object can be updated.  
    def test_update_piloto_fields(self):
        piloto = Piloto.objects.create(id=10, nombre="Lewis", apellidos="Hamilton", fecha_nacimiento="1985-01-07 00:00:00", nacionalidad="British", abreviatura="HAM", activo=True, enlace="https://www.lewishamilton.com/")
        piloto.nombre = "Max"
        piloto.apellidos = "Verstappen"
        piloto.save()
        assert piloto.nombre == "Max"
        assert piloto.apellidos == "Verstappen"
    
    # Tests that a Piloto object can be deleted.  
    def test_delete_piloto(self):
        piloto = Piloto.objects.create(id=11, nombre="Lewis", apellidos="Hamilton", fecha_nacimiento="1985-01-07 00:00:00", nacionalidad="British", abreviatura="HAM", activo=True, enlace="https://www.lewishamilton.com/")
        piloto.delete()
        assert not Piloto.objects.filter(id=11).exists()
    
    # Tests that the id field of a Piloto object is unique.  
    def test_piloto_id_uniqueness(self):
        Piloto.objects.create(id=12, nombre="Lewis", apellidos="Hamilton", fecha_nacimiento="1985-01-07 00:00:00", nacionalidad="British", abreviatura="HAM", activo=True, enlace="https://www.lewishamilton.com/")
        with self.assertRaises(Exception):
            Piloto.objects.create(id=12, nombre="Max", apellidos="Verstappen", fecha_nacimiento="1997-09-30 00:00:00", nacionalidad="Dutch", abreviatura="VER", activo=True, enlace="https://www.verstappen.nl/")
    ################### CARGA DE PILOTOS #####################
    
    # Tests that the function loads all drivers successfully. 
    def test_load_drivers_happy_pah(self):

        # Lee del dataset, siendo  859 el número de pilotos que hay 
        
        assert load_drivers() == 859

        ############ VISTAS ############
    def test_list_drivers_default(self):
        # Happy path test for displaying all drivers sorted by active status
        request = self.mocker
        request.method = 'GET'
        request.GET = {'page': 1}
        drivers = [Piloto(nombre='Driver2', activo=1), Piloto(nombre='Driver1', activo=0)]
        self.mocker.patch('DataAnalytics.views.Piloto.objects.all', return_value=drivers)
        self.mocker.patch('DataAnalytics.views.Paginator')
        self.mocker.patch('DataAnalytics.views.settings.STATIC_URL', return_value='static/')
        response = self.client.get('/drivers/?page=1')
            
        assert response.status_code == 200
        assert len(response.context['page_obj'].object_list) == len(drivers)
        assert response.context['pages'] == []
        assert response.context['search'] == False
        assert isinstance(response.context['formulario'], PilotoBusquedaForm)
        assert response.context['STATIC_URL'] == '/static/'


    

