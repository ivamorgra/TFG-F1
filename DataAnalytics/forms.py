#encoding:utf-8
from django import forms
   
class CircuitoBusquedaForm(forms.Form):
    input = forms.CharField(label="Nombre o país del circuito", widget=forms.TextInput(attrs={'placeholder': 'Jarama/Spain'}), required=True)

'''
class PeliculaBusquedaForm(forms.Form):
    idPelicula = forms.CharField(label="Id de Pelicula", widget=forms.TextInput, required=True)

'''