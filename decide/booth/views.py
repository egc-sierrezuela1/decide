import json
import datetime
from django.http.response import HttpResponseRedirect
from django.views.generic import TemplateView, FormView
from django.conf import settings
from django.http import Http404, request, HttpResponse
from django.urls import reverse
from django.utils import timezone

from rest_framework import generics, status
from rest_framework.response import Response

from base import mods
from booth.forms import SugerenciaVotoForm, PreguntaForm, SugerenciaForm
from django.shortcuts import render
from django.template import RequestContext

from booth.models import Sugerencia

from census.models import Census

class Inicio(TemplateView):
    template_name = '/booth/inicio.html'

    def get_pagina_inicio(request):
        template = 'booth/inicio.html'
        user_actual = request.user
        num_censos_votante_actual = Census.objects.all().filter(voter_id=user_actual.id).count()
        censos_votante_actual = Census.objects.all().filter(voter_id=user_actual.id)
        return render(request, template, {"censos": censos_votante_actual, "num_censos":num_censos_votante_actual, "user":user_actual})


# TODO: check permissions and census
class BoothView(TemplateView):
    template_name = 'booth/booth.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vid = kwargs.get('voting_id', 0)

        try:
            r = mods.get('voting', params={'id': vid})

            # Casting numbers to string to manage in javascript with BigInt
            # and avoid problems with js and big number conversion
            for k, v in r[0]['pub_key'].items():
                r[0]['pub_key'][k] = str(v)

            context['voting'] = json.dumps(r[0])
        except:
            raise Http404

        context['KEYBITS'] = settings.KEYBITS

        return context



#Clase sugerencia de voto para después de rellenar el voto aparezca el formulario de sugerencia
class SugerenciaVista(FormView):
    template_name = 'booth/sugerenciaform.html'
    #form_class = SugerenciaForm
    #success_url = '/'

    def sugerencia_de_voto(request):

        if request.method=='POST':
            formulario = SugerenciaForm(request.POST)
            if formulario.is_valid():
                formulario.save()
                return HttpResponseRedirect("/booth/")
        else:
            formulario = SugerenciaForm()
        return render(request, 'booth/sugerenciaform.html', {'formulario': formulario})




def send_suggesting_form(request):

    if request.method == 'POST':
        user_id = request.user.pk
        title = request.POST['suggesting-title']
        str_s_date = request.POST['suggesting-date']
        content = request.POST['suggesting-content']
        send_date = timezone.now().date()

        s_date = datetime.datetime.strptime(str_s_date, '%Y-%m-%d').date()

        if s_date > timezone.now().date():
            s = Sugerencia(user_id=user_id, title=title, suggesting_date=s_date, content=content, send_date=send_date)
            s.save()
            return HttpResponseRedirect(reverse('pagina-inicio'))
        else:
            request.session['title'] = title
            request.session['suggesting_date'] = str_s_date
            request.session['content'] = content
            request.session['errors'] = "La fecha seleccionada ya ha pasado. Debe seleccionar una posterior al día de hoy."
            return HttpResponseRedirect(reverse('pagina-inicio'))
    else:
        return HttpResponseRedirect(reverse('pagina-inicio'))

def is_future_date(date):
    return date > timezone.now().date()

def check_unresolved_post_data(session):
    context = {}

    if 'title' in session and 'suggesting_date' in session and 'content' in session and 'errors' in session:
        context['title'] = session['title']
        context['suggesting_date'] = session['suggesting_date']
        context['content'] = session['content']
        context['errors'] = session['errors']
        del session['title']
        del session['suggesting_date']
        del session['content']
        del session['errors']

    return context

