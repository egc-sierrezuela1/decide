from django.db import models

# Create your models here.


class Pregunta(models.Model):
    nombre = models.CharField(max_length=50)

    def __str__(self):
	    return self.nombre



class SugerenciaVoto(models.Model):
    titulo = models.CharField(max_length=50)
    campos_preguntas = models.IntegerField()
    preguntas = models.ForeignKey(Pregunta, on_delete = models.CASCADE)

    def __str__(self):
	    return self.titulo


