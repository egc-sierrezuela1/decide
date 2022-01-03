import datetime

from django.test import TestCase
from django.test.client import Client, RequestFactory
from .models import Sugerencia
from voting.models import Question, QuestionOption, Voting
from census.models import Census
from store.models import Vote
from .views import check_unresolved_post_data, is_future_date, send_suggesting_form
from rest_framework.test import APIClient
from django.contrib.auth.models import User

from django.urls import reverse
from django.conf import settings
from django.utils import timezone
import requests

from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from base.tests import BaseTestCase


from mixnet.models import Auth
from base import mods

NOW_DATE = timezone.now().date()
S_DATE = NOW_DATE + datetime.timedelta(weeks=1)
M_DATE = NOW_DATE - datetime.timedelta(days=31)
E_DATE = NOW_DATE - datetime.timedelta(weeks=1)

#--------------------------------------TEST LOGIN---------------------------------------------
class LoginTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        mods.mock_query(self.client)
        u = User(id=1, username='voter1')
        u.set_password('1234')
        u.save()
        token= mods.post('authentication', entry_point='/login/', json={'username':'voter1', 'password': '1234'})
        #Add session token
        session = self.client.session
        session['user_token'] = token
        session['voter_id']=u.id
        session['username']=u.username
        session.save()

    def tearDown(self):
        super().tearDown()

    def test_get_logout(self):
        session = self.client.session
        response = self.client.get(reverse('logout'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual('user_token' in session, False)
        self.assertEqual('voter_id' in session, False)
        self.assertEqual('username' in session, False)
    
    
#--------------------------------------TEST FORMULARIO SUGERENCIA---------------------------------------------
class FormSugerenciaTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.request_factory = RequestFactory()
        self.user = User.objects.create(username="User", password="password", email="ejemplo@gmail.com")
        self.client.force_authenticate(user=self.user)


    def tearDown(self):
        super().tearDown()


    def test_was_published_recently_more_than_month(self):
        now = timezone.now().date()
        past_date = now - datetime.timedelta(weeks=4, days=1)
        past_suggesting_form = Sugerencia(send_date=past_date, suggesting_date=now)
        self.assertIs(past_suggesting_form.was_published_recently(), False)


    def test_was_published_recently_last_week(self):
        now = timezone.now().date()
        past_date = now - datetime.timedelta(weeks=1)
        past_suggesting_form = Sugerencia(send_date=past_date, suggesting_date=now)
        self.assertIs(past_suggesting_form.was_published_recently(), True)


    def test_send_suggesting_form_success(self):

        
        future_date = timezone.now().date() + datetime.timedelta(weeks=1)
        date = future_date.strftime("%Y-%m-%d")

        data = {'suggesting-title': 'Suggesting', 'suggesting-date': date, 'suggesting-content': 'Full suggesting content...'}

        request = self.request_factory.post('booth/sugerenciaformulario/send', data)
        request.user = self.user #le meto el usuario a mano

        initital_suggesting_counter = Sugerencia.objects.all().count()

        response = send_suggesting_form(request)

        afterpost_suggesting_counter = Sugerencia.objects.all().count()


        self.assertEqual(afterpost_suggesting_counter, initital_suggesting_counter + 1)
        #self.assertEqual(response.status_code, 200) #-> no devuelve un 200 porque le metemos el controlador a mano, pero hace el post que es lo que queriamos probar


    def test_send_suggesting_form_with_error(self):
        data = {'suggesting-title': 'Suggestsing', 'suggesting-date': '2020-12-01', 'suggesting-content': 'Full suggesting content...'}
        initital_suggesting_counter = Sugerencia.objects.all().count()

        response = self.client.post('/booth/sugerenciaformulario/send/', data, follow=True)

        afterpost_suggesting_counter = Sugerencia.objects.all().count()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(afterpost_suggesting_counter, initital_suggesting_counter)

 
    def test_send_suggesting_form_not_post_method(self):
        response = self.client.get('/booth/sugerenciaformulario/send/')
        self.assertEqual(response.status_code, 302)


    def test_check_unresolved_post_data(self):
        context = {}
        session = self.client.session
        session['title'] = "Suggesting title"
        session['suggesting_date'] = "2020-12-01"
        session['content'] = "Suggesting content..."
        session['errors'] = "Suggesting error msg!"
        session.save()

        context['post_data'] = check_unresolved_post_data(session)

        self.assertEqual(context['post_data']['title'], "Suggesting title")
        self.assertEqual('title' in session, False)
        self.assertEqual('suggesting_date' in session, False)
        self.assertEqual('content' in session, False)
        self.assertEqual('errors' in session, False)


    def test_check_unresolved_post_data_with_empty_session(self):
        context = {}
        session = self.client.session

        context['post_data'] = check_unresolved_post_data(session)

        self.assertEqual(not context['post_data'], True)


    def test_is_future_date_with_past_date(self):
        date = timezone.now().date() - datetime.timedelta(weeks=1)
        self.assertEqual(is_future_date(date), False)


    def test_is_future_date_with_now_date(self):
        date = timezone.now().date()
        self.assertEqual(is_future_date(date), False)


    def test_is_future_date_with_future_date(self):
        date = timezone.now().date() + datetime.timedelta(weeks=1)
        self.assertEqual(is_future_date(date), True)
