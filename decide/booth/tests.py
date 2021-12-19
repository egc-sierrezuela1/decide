from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth.models import User

from django.urls import reverse
from django.conf import settings


from mixnet.models import Auth
from base import mods

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
    
    
