from django.urls import path
from .views import BoothView, SugerenciaView


urlpatterns = [
    path('<int:voting_id>/', BoothView.as_view()),
    path('<int:voting_id>/sugerenciaformulario', SugerenciaView.sugerencia_voto),
    path('sugerenciaformulario', SugerenciaView.sugerencia_voto)
]
