import json

from random import choice

from locust import (
    HttpUser,
    SequentialTaskSet,
    TaskSet,
    task,
    between
)


HOST = "http://localhost:8000"
VOTING = 1


class DefVisualizer(TaskSet):

    @task
    def index(self):
        self.client.get("/visualizer/{0}/".format(VOTING))


class DefVoters(SequentialTaskSet):

    def on_start(self):
        with open('voters.json') as f:
            self.voters = json.loads(f.read())
        self.voter = choice(list(self.voters.items()))

    @task
    def login(self):
        username, pwd = self.voter
        self.token = self.client.post("/authentication/login/", {
            "username": username,
            "password": pwd,
        }).json()

    @task
    def getuser(self):
        self.usr= self.client.post("/authentication/getuser/", self.token).json()
        print( str(self.user))

    @task
    def voting(self):
        headers = {
            'Authorization': 'Token ' + self.token.get('token'),
            'content-type': 'application/json'
        }
        self.client.post("/store/", json.dumps({
            "token": self.token.get('token'),
            "vote": {
                "a": "12",
                "b": "64"
            },
            "voter": self.usr.get('id'),
            "voting": VOTING
        }), headers=headers)


    def on_quit(self):
        self.voter = None

class Visualizer(HttpUser):
    host = HOST
    tasks = [DefVisualizer]
    wait_time = between(3,5)



class Voters(HttpUser):
    host = HOST
    tasks = [DefVoters]
    wait_time= between(3,5)
    


#TEST DE CARGA PARA SUGERENCIA
class DefSugerencia(SequentialTaskSet):

    def on_start(self):
        with open('voters.json') as f:
            self.voters = json.loads(f.read())
        self.voter = choice(list(self.voters.items()))

    @task(1)
    def login(self):
        r = self.client.get('/booth/')
        username, pwd = self.voter
        self.token = self.client.post('/booth/login/', 
        {"username": username, 'password': pwd,
        'csrfmiddlewaretoken': r.cookies['csrftoken']})

    @task(2)
    def postFormularioSugerencia(self):
        r = self.client.get("/booth/sugerenciaformulario/")

        self.client.post("/booth/sugerenciaformulario/send/", {
            "suggesting-title": "Ejemplo de sugerencia",
            "suggesting-date": "2030-12-12",
            "suggesting-content": "Esto es una prueba de locust para las sugerencias",
            'csrfmiddlewaretoken': r.cookies['csrftoken']
        })
        #print( str(self.form2))

    def on_quit(self):
        self.voter = None


class Sugerencias(HttpUser):
    host = HOST
    tasks = [DefSugerencia]
    wait_time= between(3,5)
