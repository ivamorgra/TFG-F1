from DataAnalytics.models import Piloto
from DataAnalytics.views import list_drivers
from DataAnalytics.forms import PilotoBusquedaForm


    # Tests that the function displays all drivers sorted by active status when the page is accessed. 
def test_list_drivers_default(self, mocker):
        # Happy path test for displaying all drivers sorted by active status
        request = mocker.Mock()
        request.method = 'GET'
        request.GET = {'page': 1}
        drivers = [Piloto(nombre='Driver1', activo=True), Piloto(nombre='Driver2', activo=False)]
        mocker.patch('DataAnalytics.views.Piloto.objects.all', return_value=drivers)
        mocker.patch('DataAnalytics.views.Paginator')
        mocker.patch('DataAnalytics.views.settings.STATIC_URL', return_value='static/')
        response = list_drivers(request)
        assert response.status_code == 200
        assert response.context_data['page_obj'].object_list == drivers
        assert response.context_data['pages'] == []
        assert response.context_data['search'] == False
        assert isinstance(response.context_data['formulario'], PilotoBusquedaForm)
        assert response.context_data['drivers'] == drivers
        assert response.context_data['STATIC_URL'] == 'static/'