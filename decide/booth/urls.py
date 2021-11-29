from django.urls import path
from .views import BoothView, SugerenciaView, SugerenciaVista


urlpatterns = [
    path('<int:voting_id>/', BoothView.as_view()),
    #path('<int:voting_id>/sugerenciaformulario', SugerenciaView.sugerencia_de_voto),
    path('<int:voting_id>/sugerenciaformulario', SugerenciaVista.sugerencia_de_voto),
    #path('sugerenciaformulario', SugerenciaView.sugerencia_voto)
]
