from django.forms import ModelForm
from django import forms

from booth.models import Sugerencia

# Create your forms here.


class SugerenciaForm(ModelForm):

    class Meta:
        model = Sugerencia
        fields = "__all__"
