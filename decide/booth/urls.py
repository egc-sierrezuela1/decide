from django.urls import path
from .views import BoothView, SugerenciaVista, Inicio, send_suggesting_form


urlpatterns = [
    path('', Inicio.get_pagina_inicio, name="pagina-inicio"),
    path('<int:voting_id>/', BoothView.as_view(), name="votacion"),
    path('sugerenciaformulario/', SugerenciaVista.sugerencia_de_voto),
    path('sugerenciaformulario/send/', send_suggesting_form, name="suggesting-send")
]
