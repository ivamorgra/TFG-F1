from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By

from DataAnalytics.models import Piloto


class DriverViewTestCase(StaticLiveServerTestCase):

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

        # Opciones de selenium
        options = webdriver.ChromeOptions()
        options.headless = False
        self.driver = webdriver.Chrome(options=options)
        self.driver.set_window_size(1920, 1080)

    def tearDown(self):
        self.driver.quit()
            
        super().tearDown()

    #Test en el que nos aseguramos de que se cargue correctamente el listado en la vista (tabla)
    def test_list_driver_view(self):
        # check fix/730: PAYMENT FORM NOT MANTAINING SUBJECT

        # Acess form from list
        self.driver.get(f"{self.live_server_url}/drivers/?page=1")
        # await until add-payment a is loaded
        
        abreviatura = self.driver.find_element(By.XPATH,"//td[@id='driver-ab']/a/dd ")
        nombre = self.driver.find_element(By.XPATH,"//td[@id='driver-name']")
        apellidos = self.driver.find_element(By.XPATH,"//td[@id='driver-apellidos']")
        nacionalidad = self.driver.find_element(By.XPATH,"//td[@id='driver-nacionalidad']")
        

        # En la tabla, el primer elemento (fila) es la del ultimo Piloto creado en el setup
        assert abreviatura.text == "DT"
        assert nombre.text == "Driver2"
        assert apellidos.text == "Test2"
        assert nacionalidad.text == "Spanish"
