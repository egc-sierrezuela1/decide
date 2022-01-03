import datetime

from django.test import TestCase
from django.test.client import Client, RequestFactory
from .models import Sugerencia
from voting.models import Question, QuestionOption, Voting
from census.models import Census
from store.models import Vote
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from booth.tests import LoginTest

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