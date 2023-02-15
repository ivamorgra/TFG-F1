#encoding:utf-8
from django import forms
   
class CircuitoBusquedaForm(forms.Form):
    input = forms.CharField(label="Nombre o país del circuito", widget=forms.TextInput(attrs={'placeholder': 'Jarama/Spain'}), required=True)


class ConstructorBusquedaForm(forms.Form):
    input = forms.CharField(label="Nombre o país de la escudería", widget=forms.TextInput(attrs={'placeholder': 'Ferrari/Italian'}), required=True)

class PilotoBusquedaForm(forms.Form):
    input = forms.CharField(label="Nombre o país de la escudería", widget=forms.TextInput(attrs={'placeholder': 'Fernando Alonso/Spanish'}), required=True)

class CarreraBusquedaForm(forms.Form):
    input = forms.CharField(label="Temporada o Nombre del Gran Premio", widget=forms.TextInput(attrs={'placeholder': 'Chinese Grand Prix/2005'}), required=True)