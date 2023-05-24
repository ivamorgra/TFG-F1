from django.test import TestCase
from requests import patch
from DataAnalytics.models import Circuito
from unittest.mock import Mock
from DataAnalytics import spark_loader
from DataAnalytics.models import Piloto
from DataAnalytics.spark_queries import driver_basic_stats, get_num_wins_driver, get_race_podium
from pyspark.sql import SparkSession
import pytest
from DataAnalytics.trends import search_trends

from DataAnalytics.twitter import TwitterAuth, TwitterClient, UserClient

class CircuitoTest(TestCase):
    def setUp(self):
        self.circuit1 = Circuito.objects.create(
            id = 1,
            nombre = 'Circuito1',
            nombre_referencia = 'Circuito_1',
            localizacion = 'Spain',
            pais = 'Spain',
            longitud = 1.0,
            altura = 1.0,
            latitud = 1.0,
            enlace = 'https://www.circuito1.com/',
            
        )   
        self.circuit2 = Circuito.objects.create(
            id = 2,
            nombre = 'Circuito2',
            nombre_referencia = 'Circuito_2',
            localizacion = 'Spain',
            pais = 'Spain',
            longitud = 1.0,
            altura = 1.0,
            latitud = 1.0,
            enlace = 'https://www.circuito2.com/',
            
        )
        self.mocker = Mock()

    def test_retrieve_circuit_name(self):
        circuit = Circuito.objects.get(id=1)
        self.assertEqual(circuit.nombre, 'Circuito1')
    
    def test_retrieve_all_circuits(self):
        circuit = Circuito.objects.all()
        self.assertEqual(circuit.count(), 2)
    
    def test_delete_circuit(self):
        circuit = Circuito.objects.get(id=1)
        circuit.delete()
        self.assertEqual(Circuito.objects.all().count(), 1)
    
    def test_create_circuit_with_required_fields(self):
        circuit = Circuito.objects.create(
            id=3,
            nombre="Circuito3",
            nombre_referencia="Circuito_3",
            localizacion="Spain",
            pais="Spain",
            longitud=1.0,
            altura=1.0,
            latitud=1.0,
            enlace="https://www.circuito3.com/",
        )
        assert circuit.id == 3
        assert circuit.nombre == "Circuito3"
        assert circuit.nombre_referencia == "Circuito_3"
        assert circuit.localizacion == "Spain"
        assert circuit.pais == "Spain"
        assert circuit.longitud == 1.0
        assert circuit.altura == 1.0
        assert circuit.latitud == 1.0
        assert circuit.enlace == "https://www.circuito3.com/"
    
    def test_update_circuit(self):
        circuit = Circuito.objects.get(id=1)
        circuit.nombre = 'Circuito1_updated'
        circuit.save()
        self.assertEqual(Circuito.objects.get(id=1).nombre, 'Circuito1_updated')
    
    def test_circuit_str(self):
        circuit = Circuito.objects.get(id=1)
        self.assertEqual(str(circuit), 'Circuito1')
    
    def test_circuit_repr(self):
        circuit = Circuito.objects.get(id=1)
        self.assertEqual(repr(circuit), '<Circuito: Circuito1>')
        
    def test_update_circuit_fields(self):
        circuit = Circuito.objects.get(id=1)
        circuit.nombre = 'Circuito1_updated'
        circuit.nombre_referencia = 'Circuito_1_updated'
        circuit.localizacion = 'Spain_updated'
        circuit.pais = 'Spain_updated'
        circuit.longitud = 2.0
        circuit.altura = 2.0
        circuit.latitud = 2.0
        circuit.enlace = 'https://www.circuito1_updated.com/'
        circuit.save()
        self.assertEqual(Circuito.objects.get(id=1).nombre, 'Circuito1_updated')
        self.assertEqual(Circuito.objects.get(id=1).nombre_referencia, 'Circuito_1_updated')
        self.assertEqual(Circuito.objects.get(id=1).localizacion, 'Spain_updated')
        self.assertEqual(Circuito.objects.get(id=1).pais, 'Spain_updated')
        self.assertEqual(Circuito.objects.get(id=1).longitud, 2.0)
        self.assertEqual(Circuito.objects.get(id=1).altura, 2.0)
        self.assertEqual(Circuito.objects.get(id=1).latitud, 2.0)
        self.assertEqual(Circuito.objects.get(id=1).enlace, 'https://www.circuito1_updated.com/')
    
        # Tests that the function returns the correct list of 4 integers for a driver with existing regular and sprint races.
    def test_driver_basic_stats_happy(self):
        # Mocking the spark.read.csv method to return a small dataset with regular and sprint races for a driver
        spark = SparkSession.Builder().appName("F1Analytics").getOrCreate()
        spark.createDataFrame([(1, 1, 1, 1), (1, 1, 2, 0)], ['raceId', 'driverId', 'position', 'laps'])
        spark.createDataFrame([(1, 1, 1), (2, 1, 0)], ['raceId', 'driverId', 'position'])
        
        # Call the function with the mocked dataset
        stats = driver_basic_stats(1)
        #print (stats)
        # Assert that the function returns the correct list of 4 integers
        
        assert stats == [296, 103, 3, 0]

        # Tests that the function returns the correct number of wins for a driver with one win.
    def test_happy_path_single_win(self):

        driver_id = 1

        result = get_num_wins_driver(driver_id)
        assert result == 103
    
        # Tests that get_user_timeline_tweets returns an empty list when num_tweets is 0.
    def test_get_user_timeline_tweets_zero(self):
        client = TwitterClient("test_user")
        assert client.get_user_timeline_tweets(0) == []

    
        # Tests that Twitter API authentication is successful.
    def test_authenticate_twitter_app_success(self):
        client = UserClient()
        assert client.auth is not None
        assert client.twitter_client is not None

        # Tests that the function returns correct values for valid keyword and days inputs.
    def test_happy_path_valid_inputs(self):
        keyword = "Python"
        days = 60
        months, valores, media, total, countries, values = search_trends(keyword, days)
        assert len(months) == 3
        assert len(valores) == 3
        assert media > 0
        assert total > 0
        assert len(countries) == 10
        assert len(values) == 10
    
        # Tests that the function correctly handles days input less than or equal to 30.
    def test_edge_case_days_less_than_30(self):
        keyword = "Java"
        days = 15
        months, valores, media, total, countries, values = search_trends(keyword, days)
    
        assert len(months) == 12
        assert len(valores) == 12
        assert media > 0
        assert total > 0
        assert len(countries) == 10
        assert len(values) == 10
    
        # Tests that the function correctly handles empty or invalid keyword input.
    def test_edge_case_invalid_keyword(self):
        keyword = ""
        days = 30
        with pytest.raises(Exception):
            search_trends(keyword, days)