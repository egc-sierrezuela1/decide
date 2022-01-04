import json
from datetime import datetime
from django.http.response import HttpResponseRedirect
from django.views.generic import TemplateView, FormView
from django.conf import settings
from django.http import Http404, request, HttpResponse
from django.urls import reverse
from django.utils import timezone

from rest_framework import generics, status
from rest_framework.response import Response

from base import mods
from booth.forms import SugerenciaForm
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
        if acceso[1] is not None:
            usuario = User.objects.all().filter(id=acceso[1])[0]
            if acceso[0]:
                login(request, usuario)
                return (HttpResponseRedirect(reverse('pagina-inicio')))
                     
    return render(request, 'booth/login.html', {'formulario':formulario, 'STATIC_URL':settings.STATIC_URL})

def check_user_has_voted(context, voting_id, voter_id):
    number_of_votes = Vote.objects.filter(voting_id=voting_id,voter_id=voter_id).count()
    if number_of_votes !=0:
        context['voted'] = True

def logout_view(request):
    logout(request)
    print(request.user)
    return HttpResponseRedirect(reverse('pagina-inicio'))

@login_required(login_url="/booth/login")
def get_pagina_inicio(request):
    res = []
    sol = []
    template = 'booth/inicio.html'
    user_actual = request.user
    usuario_valido = User.objects.all().filter(id=user_actual.id).count()
    num_censos_votante_actual = Census.objects.all().filter(voter_id=user_actual.id).count()
    censos_votante_actual = Census.objects.all().filter(voter_id=user_actual.id)
    for censo in censos_votante_actual:
        voto_valido = Voting.objects.all().filter(id=censo.voting_id)
        if voto_valido[0].end_date != None:
            if voto_valido[0].end_date.strftime('%Y-%m-%d %H:%M') < datetime.today().strftime('%Y-%m-%d %H:%M'):
                res.append(True)
                sol.append(censo.voting_id)
        else:
            res.append(False)
            sol.append(censo.voting_id )
    x = list(zip(res,sol))
    u = []
    for t,y in x:
        if t == False:
            u.append(y)
    sol = u
    return render(request, template, {"censos": censos_votante_actual, "num_censos":num_censos_votante_actual,
            "user":user_actual, "usuario_valido": usuario_valido,"res":res,"sol":sol})

        
# TODO: check permissions and census
class BoothView(TemplateView):
    template_name = 'booth/booth.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        voting_id = kwargs.get('voting_id', 0)

        context['token'], context['voter'], voter_id = get_user(self)

        censos_votante_actual = Census.objects.all().filter(voter_id=voter_id)
        puede_votar = False
        for censo in censos_votante_actual:
            if not puede_votar:
                if voting_id == censo.voting_id:
                    puede_votar = True
        context["puede_votar"] = puede_votar#con esto nos lo llevamos a la vista


        try:
            r = mods.get('voting', params={'id': voting_id, "votar": puede_votar})

            # Casting numbers to string to manage in javascript with BigInt
            # and avoid problems with js and big number conversion
            for k, v in r[0]['pub_key'].items():
                r[0]['pub_key'][k] = str(v)

            context['voting'] = json.dumps(r[0])
            context['votos'] = Vote.objects.all().filter(voting_id=voting_id).count()
            check_user_has_voted(context, voting_id, voter_id)
        except:
            raise Http404

        context['KEYBITS'] = settings.KEYBITS

        return context

#Clase sugerencia de voto para después de rellenar el voto aparezca el formulario de sugerencia
class SugerenciaVista(FormView):
    template_name = 'booth/sugerenciaform.html'
    #form_class = SugerenciaForm
    #success_url = '/'

    @login_required(login_url="/booth/login")
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

        if is_future_date(s_date):
            s = Sugerencia(user_id=user_id, title=title, suggesting_date=s_date, content=content, send_date=send_date)
            s.save()
            return HttpResponseRedirect(reverse('pagina-inicio'))
        else:
            #no muestra el error en la vista
            request.session['title'] = title
            request.session['suggesting_date'] = str_s_date
            request.session['content'] = content
            request.session['errors'] = "La fecha seleccionada ya ha pasado. Debe seleccionar una posterior al día de hoy."
            return HttpResponseRedirect(reverse('formulario_suggest'))
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

