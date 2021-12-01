from django.urls import path, include
from .views import BoothView, SugerenciaVista, Inicio, send_suggesting_form, LogoutView, LoginView, loginformpost
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import logout, login
from rest_framework.authtoken.views import obtain_auth_token




urlpatterns = [
    path('', LoginView.as_view(), name="login"),
    path('logout/', LogoutView.as_view(), name="logout"),
    path('inicio/', loginformpost, name="login-send"),
    #path('inicio/', Inicio.get_pagina_inicio, name="pagina-inicio"),
    path('<int:voting_id>/', BoothView.as_view(), name="votacion"),
    path('inicio/sugerenciaformulario/', SugerenciaVista.sugerencia_de_voto),
    path('inicio/sugerenciaformulario/send/', send_suggesting_form, name="suggesting-send")
]
