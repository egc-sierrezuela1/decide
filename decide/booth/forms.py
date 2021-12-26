from django.forms import ModelForm
from django import forms

from booth.models import SugerenciaVoto, Pregunta, Sugerencia

# Create your forms here.


class SugerenciaVotoForm(ModelForm):
    
    class Meta:
        model = SugerenciaVoto
        fields = ['titulo', 'campos_preguntas', 'preguntas'] 


class PreguntaForm(ModelForm):

    class Meta:
        model = Pregunta
        fields = "__all__"

class SugerenciaForm(ModelForm):

    class Meta:
        model = Sugerencia
        fields = "__all__"
