from django.test import TestCase
from DataAnalytics.models import Piloto
from DataAnalytics.models import Piloto
from DataAnalytics.views import list_drivers
from DataAnalytics.forms import PilotoBusquedaForm
import unittest
from unittest.mock import MagicMock

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
        # Crea un mocker
        self.mocker = MagicMock()
        

    def test_active_drivers(self):
        self.assertEqual(Piloto.objects.all().filter(activo=1).count(), 1)
    
    def test_inactive_drivers(self):
        self.assertEqual(Piloto.objects.all().filter(activo=0).count(), 1)
    
  ##################### VISTAS #####################

    def test_list_drivers_default(self):
        # Happy path test for displaying all drivers sorted by active status
        request = self.mocker.Mock()
        request.method = 'GET'
        request.GET = {'page': 1}
        drivers = [Piloto(nombre='Driver2', activo=1), Piloto(nombre='Driver1', activo=0)]
        self.mocker.patch('DataAnalytics.views.Piloto.objects.all', return_value=drivers)
        self.mocker.patch('DataAnalytics.views.Paginator')
        self.mocker.patch('DataAnalytics.views.settings.STATIC_URL', return_value='static/')
        response = self.client.get('/drivers/?page=1')
        #response = list_drivers(request)
        assert response.status_code == 200
        assert len(response.context['page_obj'].object_list) == len(drivers)
        assert response.context['pages'] == []
        assert response.context['search'] == False
        assert isinstance(response.context['formulario'], PilotoBusquedaForm)
        assert response.context['STATIC_URL'] == '/static/'