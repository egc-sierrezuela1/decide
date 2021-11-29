from django.forms import ModelForm
from django import forms

from booth.models import SugerenciaVoto

# Create your forms here.


class SugerenciaVotoForm(ModelForm):
    
    class Meta:
        model = SugerenciaVoto
        fields = ['titulo', 'campos_preguntas', 'preguntas']


class SugerenciaVotoEjemplo(forms.Form):
    titulo = forms.CharField(label="Titulo del voto", widget=forms.TextInput, required=True)
