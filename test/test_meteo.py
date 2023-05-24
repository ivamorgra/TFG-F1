from unittest import TestCase
from DataAnalytics.meteo import get_weather
from unittest.mock import MagicMock, patch

# Dependencies:
# pip install pytest-mock
import pytest

class TestGetWeather(TestCase):
    # Tests that the function returns weather data for valid input.
    @patch('DataAnalytics.meteo')
    def test_valid_input(self, mocker):
        # Mock the API response
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "values": [
                {
                    "temp": 20,
                    "precip": 0,
                    "humidity": 50,
                    "conditions": "Sunny",
                    "mint": 15
                }
            ]
        }
        mocker.patch('requests.request', return_value=mock_response)

        # Call the function with valid input
        location = "New York"
        date = "2022-01-01T00:00:00"
        end_date = "2022-01-02T00:00:00"
        start_time = "08:00:00"
        end_time = "16:00:00"
        result = get_weather(location, date, end_date, start_time, end_time)

        # Check that the function returns the expected weather data
        assert result == [(10.2, 12.1, 2.95, 92.38, 'Rain, Overcast')]

