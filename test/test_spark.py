from unittest import TestCase
from unittest.mock import MagicMock, patch
from DataAnalytics.models import Piloto
from DataAnalytics.spark_queries import get_active_driver_byname, get_driver_avg_points_by_season, get_driver_avg_position_by_season, get_driver_max_position_by_season, get_driver_min_position_by_season, get_driver_num_races, get_driver_wins_by_season, get_race_podium, get_races


# Dependencies:
# pip install pytest-mock
import pytest


class TestSparkQueries(TestCase):

    @patch('DataAnalytics.spark_queries.spark')
    def test_get_driver_num_races(self, spark_mock):
        # Mock the necessary objects
        results_mock = MagicMock()
        results_mock.filter.return_value.count.return_value = 5
        spark_mock.read.csv.return_value = results_mock

        # Call the function
        driver_id = 1
        num_races = get_driver_num_races(driver_id)

        # Assert the result
        self.assertEqual(num_races, 5)

    @patch('DataAnalytics.spark_queries.spark')
    def test_get_driver_avg_position_by_season(self, spark_mock):
        # Mock the necessary objects
        results_mock = MagicMock()
        season_races_mock = MagicMock()
        results_join_mock = MagicMock()
        num_races_mock = MagicMock()
        positions_mock = MagicMock()

        # Configure the mock objects
        results_mock.join.return_value = results_join_mock
        results_join_mock.filter.return_value = num_races_mock
        num_races_mock.groupBy.return_value.agg.return_value = positions_mock
        positions_mock.orderBy.return_value.first.return_value = ('1', 10)

        # Configure the spark mock to return the mock objects
        spark_mock.read.csv.side_effect = [results_mock, season_races_mock]

        # Call the function
        driver_id = 1
        season = 2022
        position, count = get_driver_avg_position_by_season(driver_id, season)

        # Assert the result
        self.assertEqual(position, '1')
        self.assertEqual(count, 10)

    @patch('DataAnalytics.spark_queries.spark')
    def test_get_driver_max_position_by_season(self, spark_mock):
            # Mock the necessary objects
            results_mock = MagicMock()
            season_races_mock = MagicMock()
            results_join_mock = MagicMock()
            num_races_mock = MagicMock()

            # Configure the mock objects
            results_mock.join.return_value = results_join_mock
            results_join_mock.filter.return_value = num_races_mock
            num_races_mock.orderBy.return_value.first.return_value = ('3', 'Driver C', '2022', '3')


            # Configure the spark mock to return the mock objects
            spark_mock.read.csv.side_effect = [results_mock, season_races_mock]

            # Call the function
            driver_id = 1
            season = 2022
            position = get_driver_max_position_by_season(driver_id, season)
            
            # Assert the result
            self.assertEqual(position[0], '3')

    @patch('DataAnalytics.spark_queries.spark')
    def test_get_driver_min_position_by_season(self, spark_mock):
        # Mockear los objetos necesarios
        results_mock = MagicMock()
        season_races_mock = MagicMock()
        results_join_mock = MagicMock()
        num_races_mock = MagicMock()

        # Configurar los objetos mockeados
        results_mock.join.return_value = results_join_mock
        results_join_mock.filter.return_value = num_races_mock
        num_races_mock.orderBy.return_value.first.return_value = ('1', 'Driver A', '2022', '1')

        # Configurar el mock de spark para devolver los objetos mockeados
        spark_mock.read.csv.side_effect = [results_mock, season_races_mock]

        # Llamar a la función
        driver_id = 1
        season = 2022
        position = get_driver_min_position_by_season(driver_id, season)

        # Verificar el resultado
        self.assertEqual(position[0], '1')

    @patch('DataAnalytics.spark_queries.spark')
    def test_get_driver_avg_points_by_season(self, spark_mock):
        # Mockear los objetos necesarios
        results_mock = MagicMock()
        season_races_mock = MagicMock()
        results_join_mock = MagicMock()
        num_races_mock = MagicMock()
        avg_points_mock = MagicMock()

        # Configurar los objetos mockeados
        results_mock.join.return_value = results_join_mock
        results_join_mock.filter.return_value = num_races_mock
        num_races_mock.agg.return_value = avg_points_mock
        avg_points_mock.first.return_value = (3.14,)

        # Configurar el mock de spark para devolver los objetos mockeados
        spark_mock.read.csv.side_effect = [results_mock, season_races_mock]

        # Llamar a la función
        driver_id = 1
        season = 2022
        avg_points = get_driver_avg_points_by_season(driver_id, season)

        # Verificar el resultado
        self.assertEqual(avg_points, 3.14)

    @patch('DataAnalytics.spark_queries.spark')
    def test_get_driver_wins_by_season(self, spark_mock):
        # Mockear los objetos necesarios
        results_mock = MagicMock()
        season_races_mock = MagicMock()
        results_join_mock = MagicMock()
        wins_mock = MagicMock()

        # Configurar los objetos mockeados
        results_mock.join.return_value = results_join_mock
        results_join_mock.filter.return_value = wins_mock
        wins_mock.count.return_value = 5

        # Configurar el mock de spark para devolver los objetos mockeados
        spark_mock.read.csv.side_effect = [results_mock, season_races_mock]

        # Llamar a la función
        driver_id = 1
        season = 2022
        wins = get_driver_wins_by_season(driver_id, season)

        # Verificar el resultado
        self.assertEqual(wins, 5)

    def test_get_active_driver_byname(self):
        # Crear un piloto activo para el test
        active_driver = Piloto.objects.create(id=30,nombre="Driver", apellidos="Active",fecha_nacimiento="1999-08-09", activo=True)

        # Llamar a la función con el nombre del piloto activo
        driver_name = "Active"
        driver = get_active_driver_byname(driver_name)

        # Verificar el resultado
        self.assertEqual(driver, active_driver)

    def test_get_inactive_driver_byname(self):
        # Crear un piloto inactivo para el test
        Piloto.objects.create(id=20,nombre="Driver", apellidos="Inactive",fecha_nacimiento="1999-08-09", activo=False)

        # Llamar a la función con el nombre del piloto inactivo
        driver_name = "Inactive"
        driver = get_active_driver_byname(driver_name)

        # Verificar el resultado
        self.assertIsNone(driver)

    @patch('DataAnalytics.spark_queries.spark.read.csv')

    #@patch('DataAnalytics.spark_queries.spark')
    def test_get_races(self, mock_read_csv):
        # Configurar los datos de prueba

        # Llamar a la función
        races = get_races()

        # Verificar los resultados
        expected_races = [
            ("1097", 'Bahrain Grand Prix', "2023",)
        ]
        self.assertEqual(races[0], expected_races[0])
        
        '''
        # Crear una instancia de DataFrame simulado con Spark
        spark_dataframe_mock = MagicMock()
        spark_dataframe_mock.read.csv.return_value = spark_dataframe_mock
        spark_dataframe_mock.select.return_value = spark_dataframe_mock
        spark_dataframe_mock.withColumn.return_value = spark_dataframe_mock
        spark_dataframe_mock.filter.return_value = spark_dataframe_mock
        spark_dataframe_mock.collect.return_value = race_data

        # Configurar el mock de spark para devolver el DataFrame simulado
        with patch('DataAnalytics.spark_queries.spark', return_value=spark_dataframe_mock):
            # Llamar a la función
            races = get_races()

            # Verificar el resultado
            expected_result = [
                (3, "Race 3", 2023, "01/03/23"),
                (2, "Race 2", 2022, "01/02/22"),
                (1, "Race 1", 2022, "01/01/22"),
            ]
            self.assertEqual(races, expected_result)
        '''

    def test_get_top3drivers_evolution(self):
        # Llama a la función get_top3drivers_evolution con los datos de prueba
        # Comprueba que los resultados sean los esperados

        # Ejemplo:
        abreviaturas = ['ABR1', 'ABR2', 'ABR3']
        races, names_races, puntuation_driver1, puntuation_driver2, puntuation_driver3 = get_top3drivers_evolution(abreviaturas)

        # Asegúrate de que los resultados sean los esperados
        self.assertEqual(len(races), 10)  # Comprueba el número de carreras
        self.assertEqual(len(names_races), 10)  # Comprueba el número de nombres de carreras
        self.assertEqual(len(puntuation_driver1), 10)  # Comprueba el número de puntos del piloto 1
        # Continúa con las aserciones para los demás resultados esperados







