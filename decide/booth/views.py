import json
from django.http.response import HttpResponseRedirect
from django.views.generic import TemplateView, FormView
from django.conf import settings
from django.http import Http404, request, HttpResponse

from rest_framework import generics, status
from rest_framework.response import Response

from base import mods
from booth.forms import SugerenciaVotoForm, PreguntaForm, SugerenciaForm
from django.shortcuts import render
from django.template import RequestContext


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
class SugerenciaView(FormView):
    template_name = 'booth/sugerencia.html'
    form_class = SugerenciaVotoForm
    success_url = '/'

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        form.send_email()
        return super().form_valid(form) 

    def sugerencia_voto(request, voting_id):
        if request=='POST':
            formulario = SugerenciaVotoForm(request.POST)
            formulario2 = PreguntaForm(request.POST)
            if formulario.is_valid() & formulario2.is_valid():
                nueva_sugerencia = formulario.save()
                nueva_pregunta = formulario2.save()
                return HttpResponseRedirect("/")
        else:
            formulario = SugerenciaVotoForm()
            formulario2 = PreguntaForm()
        return render(request, 'booth/sugerencia.html', {'formulario': formulario, 'formulario2':formulario2, 'voting_id': voting_id})


class SugerenciaVista(FormView):
    template_name = 'booth/sugerenciaform.html'
    form_class = SugerenciaForm
    success_url = '/'

    def sugerencia_de_voto(request, voting_id):
        if request=='POST':
            formulario = SugerenciaForm(request.POST)
            if formulario.is_valid():
                nueva_sugerencia = formulario.save()
                return HttpResponseRedirect("/")
        else:
            formulario = SugerenciaForm()
        return render(request, 'booth/sugerenciaform.html', {'formulario': formulario, 'voting_id': voting_id})

