from django.db import models

import datetime
from django.utils import timezone

# Create your models here.


class Pregunta(models.Model):
    nombre = models.CharField(max_length=50)

    def __str__(self):
	    return self.nombre



class SugerenciaVoto(models.Model):
    titulo = models.CharField(max_length=50, verbose_name="Título")
    campos_preguntas = models.PositiveSmallIntegerField(default="2")
    preguntas = models.ForeignKey(Pregunta, on_delete = models.CASCADE)

    def __str__(self):
	    return self.titulo

#Modelo adquirido del proyecto EGC-GUADALENTIN
class Sugerencia(models.Model):
    user_id = models.IntegerField()
    title = models.CharField(max_length=200, blank=False)
    suggesting_date = models.DateField(default=datetime.date.today)
    content = models.TextField(blank=False, max_length=4000)
    send_date = models.DateField(blank=False)
    is_approved = models.NullBooleanField()

    def __str__(self):
        """Imprime el título de la sugerencia de votación."""
        return self.title

    def was_published_recently(self):
        now = timezone.now().date()
        limit_date = now - datetime.timedelta(weeks=4)
        return limit_date <= self.send_date
