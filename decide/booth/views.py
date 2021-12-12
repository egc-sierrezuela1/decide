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
from voting.models import Voting
from store.models import Vote
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required



def autenticacion(request, username, password):
    token= mods.post('authentication', entry_point='/login/', json={'username':username, 'password':password})
    request.session['user_token']=token
    voter = mods.post('authentication', entry_point='/getuser/', json=token)
    voter_id = voter.get('id', None)
    request.session['voter_id'] = voter_id

    if voter_id == None:
        return False, voter_id

    return True, voter_id

def get_user(self):
    token = self.request.session.get('user_token', None)
    voter = mods.post('authentication', entry_point='/getuser/', json=token)
    voter_id = voter.get('id', None)
    return json.dumps(token.get('token', None)), json.dumps(voter), voter_id


def ingresar(request):
    if request.user.is_authenticated:
        return(HttpResponseRedirect('booth/inicio.html'))

    formulario = AuthenticationForm()
    if request.method=='POST':
        formulario = AuthenticationForm(request.POST)
        usuario=request.POST['username']
        clave=request.POST['password']

        acceso=autenticacion(request,usuario,clave)#Dice que hay un None type en request.content_type
        usuario = User.objects.all().filter(id=acceso[1])[0]
        if acceso[1] is not None:
            if acceso[0]:
                login(request, usuario)
                return (HttpResponseRedirect(reverse('pagina-inicio')))
            else:
                return render(request, 'mensaje_error.html',{'error':"USUARIO NO ACTIVO",'STATIC_URL':settings.STATIC_URL})
        else:
            return render(request, 'mensaje_error.html',{'error':"USUARIO O CONTRASEÑA INCORRECTOS",'STATIC_URL':settings.STATIC_URL})
                     
    return render(request, 'booth/login.html', {'formulario':formulario, 'STATIC_URL':settings.STATIC_URL})

def logout_view(request):
    logout(request)
    print("LOG OUT")
    print(request.user)
    return HttpResponseRedirect(reverse('pagina-inicio'))

@login_required(login_url="/booth/login")
def get_pagina_inicio(request):#/booth
    template = 'booth/inicio.html'
    user_actual = request.user
    #request.user = user_actual#para guardar en el request el usuario que se ha autenticado :)
    usuario_valido = User.objects.all().filter(id=user_actual.id).count()
    num_censos_votante_actual = Census.objects.all().filter(voter_id=user_actual.id).count()
    censos_votante_actual = Census.objects.all().filter(voter_id=user_actual.id)
    return render(request, template, {"censos": censos_votante_actual, "num_censos":num_censos_votante_actual,
            "user":user_actual, "usuario_valido": usuario_valido})
        
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

            context['votos'] = Vote.objects.all().filter(voting_id=vid).count()
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
        user_id = request.user.id
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
            return HttpResponseRedirect(reverse('formulario_suggest'))
    else:
        return HttpResponseRedirect(reverse('booth/inicio.html'))

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

