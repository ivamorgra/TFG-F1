from django.test import TestCase
from requests import patch
from DataAnalytics.models import Constructor
from DataAnalytics.spark_loader import load_drivers
from DataAnalytics.forms import ConstructorBusquedaForm
from unittest.mock import Mock

class ConstructorTest(TestCase):
    def setUp(self):
        
        self.constructor = Constructor.objects.create(
            id = 1,
            nombre = 'Constructor1',
            nacionalidad = 'Spanish',
            enlace = 'https://www.constructor1.com/',
            referencia = 'C1',
            activo = 0,
        )
        #self.constructor.save()
        self.constructor2 = Constructor.objects.create(
            id = 2,
            nombre = 'Constructor2',
            nacionalidad = 'Spanish',
            enlace = 'https://www.constructor2.com/',
            referencia = 'C2',
            activo = 1,
        )   
        
        #self.constructor2.save()
        self.mocker = Mock()

    def test_active_constructors(self):
        self.assertEqual(Constructor.objects.all().filter(activo=1).count(), 1)

    def test_inactive_constructor(self):
        self.assertEqual(Constructor.objects.all().filter(activo=0).count(), 1)

    def test_create_constructor_with_required_fields(self):
        constructor = Constructor.objects.create(
            id=3,
            nombre="Mercedes",
            nacionalidad="German",
            enlace="https://www.mercedes.com/",
            referencia="MER",
            activo=True,
        )
        assert constructor.id == 3
        assert constructor.nombre == "Mercedes"
        assert constructor.nacionalidad == "German"
        assert constructor.enlace == "https://www.mercedes.com/"
        assert constructor.referencia == "MER"
        assert constructor.activo == True
        
    
    def test_retrieve_constructor_name(self):
        constructor = Constructor.objects.get(id=1)
        self.assertEqual(constructor.nombre, 'Constructor1')
    
    def test_retrieve_all_constructors(self):
        constructor = Constructor.objects.all()
        self.assertEqual(constructor.count(), 2)

    def test_retrieve_constructor_by_id(self):
        constructor = Constructor.objects.get(id=1)
        self.assertEqual(constructor.id, 1)
    
    def test_retrieve_constructor_by_name(self):
        constructor = Constructor.objects.get(nombre='Constructor1')
        self.assertEqual(constructor.nombre, 'Constructor1')
    
    def test_update_constructor(self):
        constructor = Constructor.objects.get(id=1)
        constructor.nombre = 'Constructor1Updated'
        constructor.save()
        self.assertEqual(constructor.nombre, 'Constructor1Updated')


    def test_delete_constructor(self):
        constructor = Constructor.objects.get(id=1)
        constructor.delete()
        self.assertEqual(Constructor.objects.all().count(), 1)

        
    def test_constructor_str(self):
        constructor = Constructor.objects.get(id=1)
        self.assertEqual(constructor.__str__(), 'Constructor1')
    
    def test_constructor_id_unique(self):
        constructor = Constructor.objects.get(id=1)
        self.assertEqual(constructor.id, 1)
    