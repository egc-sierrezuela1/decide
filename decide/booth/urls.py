from django.urls import path, include
from .views import BoothView, SugerenciaVista, send_suggesting_form, get_pagina_inicio, ingresar, logout_view
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import logout, login
from rest_framework.authtoken.views import obtain_auth_token




urlpatterns = [
    path('', get_pagina_inicio, name="pagina-inicio"),
    path('login/', ingresar),
    path('logout/', logout_view, name="logout"),
    path('<int:voting_id>/', BoothView.as_view(), name="votacion"),
    path('sugerenciaformulario/', SugerenciaVista.sugerencia_de_voto, name="formulario_suggest"),
    path('sugerenciaformulario/send/', send_suggesting_form, name="suggesting-send")
]
