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

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.common.exceptions import TimeoutException

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
        print("AQUIII")
        print(response.status_code)
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


    #--------------------------------------TEST NAVEGACION---------------------------------------------

class NavigationTest(StaticLiveServerTestCase):
    
    def setUp(self):
        #Load base test functionality for decide
        self.base = BaseTestCase()
        self.base.setUp()

        options = webdriver.ChromeOptions()
        options.headless = True
        self.driver = webdriver.Chrome(options=options)

        LoginTest.setUp(self)

        super().setUp()         

    def tearDown(self):           
        super().tearDown()
        self.driver.quit()
        self.base.tearDown()    

    def test_navigation_login(self):

        self.driver.get(f'{self.live_server_url}/booth/login/')
        self.driver.find_element_by_name('username').send_keys("voter1")
        self.driver.find_element_by_name('password').send_keys("1234")
        self.driver.find_element_by_id("submit").click()

        print('ENTRA AQUI: ' + self.driver.current_url)
        self.assertEquals(self.driver.current_url,f'{self.live_server_url}/booth/')

    def test_navigation_login_fail(self):
        #Comprobamos que si no se introducen datos de inicio se mantiene en la pagina de login

        self.driver.get(f'{self.live_server_url}/booth/login/')
        self.driver.find_element_by_name('username').send_keys("failvoter")
        self.driver.find_element_by_name('password').send_keys("fail")
        self.driver.find_element_by_id('submit').click()

        self.assertEquals(self.driver.current_url,f'{self.live_server_url}/booth/login/')

    def test_navigation_sugerencias_form(self):

        self.driver.get(f'{self.live_server_url}/booth/login/')
        self.driver.find_element_by_name('username').send_keys("voter1")
        self.driver.find_element_by_name('password').send_keys("1234")
        self.driver.find_element_by_id("submit").click()

        self.driver.find_element_by_id("id_sugerencias").click()

        self.driver.find_element_by_id('suggestingTitle').send_keys("Propuesta tests")
        self.driver.find_element_by_id('suggestingDate').send_keys("01-01-2023")
        self.driver.find_element_by_id('suggestingContent').send_keys("Propuesta para hacer una nueva votacion como parte de los test de navegacion")
        self.driver.find_element_by_id('submitSugForm').click()

        self.assertEquals(self.driver.current_url,f'{self.live_server_url}/booth/')

    def test_navegacion_sugerencias_form_empty_title(self):

        self.driver.get(f'{self.live_server_url}/booth/login/')
        self.driver.find_element_by_name('username').send_keys("voter1")
        self.driver.find_element_by_name('password').send_keys("1234")
        self.driver.find_element_by_id("submit").click()

        self.driver.find_element_by_id("id_sugerencias").click()

        self.driver.find_element_by_id('suggestingTitle').send_keys("")
        self.driver.find_element_by_id('suggestingDate').send_keys("01-01-2023")
        self.driver.find_element_by_id('suggestingContent').send_keys("Propuesta para hacer una nueva votacion como parte de los test de navegacion")
        self.driver.find_element_by_id('submitSugForm').click()

        self.assertEquals(self.driver.current_url,f'{self.live_server_url}/booth/sugerenciaformulario/')

    def test_navigation_sugerencias_form_empty_date(self):

        self.driver.get(f'{self.live_server_url}/booth/login/')
        self.driver.find_element_by_name('username').send_keys("voter1")
        self.driver.find_element_by_name('password').send_keys("1234")
        self.driver.find_element_by_id("submit").click()

        self.driver.find_element_by_id("id_sugerencias").click()
        
        self.driver.find_element_by_id('suggestingTitle').send_keys("Propuesta tests")
        self.driver.find_element_by_id('suggestingDate').send_keys("")
        self.driver.find_element_by_id('suggestingContent').send_keys("Propuesta para hacer una nueva votacion como parte de los test de navegacion")
        self.driver.find_element_by_id('submitSugForm').click()
        
        self.assertEquals(self.driver.current_url,f'{self.live_server_url}/booth/sugerenciaformulario/')

    def test_navigation_sugerencias_form_empty_content(self):

        self.driver.get(f'{self.live_server_url}/booth/login/')
        self.driver.find_element_by_name('username').send_keys("voter1")
        self.driver.find_element_by_name('password').send_keys("1234")
        self.driver.find_element_by_id("submit").click()

        self.driver.find_element_by_id("id_sugerencias").click()
        
        self.driver.find_element_by_id('suggestingTitle').send_keys("Propuesta tests")
        self.driver.find_element_by_id('suggestingDate').send_keys("01-01-2023")
        self.driver.find_element_by_id('suggestingContent').send_keys("")
        self.driver.find_element_by_id('submitSugForm').click()
        
        self.assertEquals(self.driver.current_url,f'{self.live_server_url}/booth/sugerenciaformulario/')

class NavigationVotingTest(StaticLiveServerTestCase):
    
    def setUp(self):
        #Load base test functionality for decide
        self.base = BaseTestCase()
        self.base.setUp()

        options = webdriver.ChromeOptions()
        options.headless = True
        self.driver = webdriver.Chrome(options=options)

        self.client = APIClient()
        mods.mock_query(self.client)
        u = User(id=1, username='voter1')
        u.set_password('1234')
        u.save()
        token= mods.post('authentication', entry_point='/login/', json={'username':'voter1', 'password': '1234'})
        #Add session token
        session = self.client.session
        session['user_token'] = token
        session.save()

        q = Question(id=2,desc='Question de prueba')
        q.save()
        for i in range(3):
            opt = QuestionOption(question=q, option='Option {}'.format(i+1))
            opt.save()

        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,defaults={'me':True,'name':'base'})
        a.save()

        v = Voting(id=1, name='Votacion de prueba',desc='Votaciones para los test', start_date=timezone.now(), question=q)
        v.save()   
        v.auths.add(a) 
        Voting.create_pubkey(v) 

        census = Census(voting_id=v.id, voter_id=u.id)
        census.save()

        super().setUp()         

    def tearDown(self):           
        super().tearDown()
        self.driver.quit()
        self.base.tearDown()

    def test_navegacion_voting_form(self):

        self.driver.get(f'{self.live_server_url}/booth/login/')
        self.driver.find_element_by_name('username').send_keys("voter1")
        self.driver.find_element_by_name('password').send_keys("1234")
        self.driver.find_element_by_id("submit").click()

        self.driver.get(f'{self.live_server_url}/booth/1')

        #Comprobamos que nos ha dejado entrar a la cabina de voto, lo que indica que la votacion existe y estamos en el censo
        self.assertEquals(self.driver.current_url,f'{self.live_server_url}/booth/1/')