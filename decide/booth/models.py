from django.db import models

import datetime
from django.utils import timezone

# Create your models here.


#Modelo adquirido del proyecto EGC-GUADALENTIN
class Sugerencia(models.Model):
    user_id = models.IntegerField()
    title = models.CharField(max_length=200, blank=False)
    suggesting_date = models.DateField(blank=False)
    content = models.TextField(blank=False, max_length=4000)
    send_date = models.DateField(default=datetime.date.today)
    is_approved = models.NullBooleanField()

    def __str__(self):
        """Imprime el título de la sugerencia de votación."""
        return self.title

    def was_published_recently(self):
        now = timezone.now().date()
        limit_date = now - datetime.timedelta(weeks=4)
        return limit_date <= self.send_date

