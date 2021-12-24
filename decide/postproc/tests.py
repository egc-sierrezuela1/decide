from django.test import TestCase

from rest_framework.test import APIClient
from rest_framework.test import APITestCase

from base import mods


class PostProcTestCase(APITestCase):

    def setUp(self):
        self.client = APIClient()
        mods.mock_query(self.client)

    def tearDown(self):
        self.client = None


    def test_identity(self):
        data = [{
            'type': 'IDENTITY',
            'options': [
                {'option': 'Option 1', 'number': 1, 'votes': 5},
                {'option': 'Option 2', 'number': 2, 'votes': 0},
                {'option': 'Option 3', 'number': 3, 'votes': 3},
                {'option': 'Option 4', 'number': 4, 'votes': 2},
                {'option': 'Option 5', 'number': 5, 'votes': 5},
                {'option': 'Option 6', 'number': 6, 'votes': 1},
            ]
        }]

        expected_result = [{
            'type': 'IDENTITY',
            'options': [
                {'option': 'Option 1', 'number': 1, 'votes': 5,
                 'postproc': 5},
                {'option': 'Option 5', 'number': 5, 'votes': 5,
                 'postproc': 5},
                {'option': 'Option 3', 'number': 3, 'votes': 3,
                 'postproc': 3},
                {'option': 'Option 4', 'number': 4, 'votes': 2,
                 'postproc': 2},
                {'option': 'Option 6', 'number': 6, 'votes': 1,
                 'postproc': 1},
                {'option': 'Option 2', 'number': 2, 'votes': 0,
                 'postproc': 0},
            ]
        }]


        response = self.client.post('/postproc/', data, format='json')
        self.assertEqual(response.status_code, 200)

        values = response.json()
        self.assertEqual(values, expected_result)



    #TEST PARA MULTIPLES PREGUNTAS--De Guadalentin
    def test_identity_multiple_questions_1(self):
        data = [{
            'type': 'IDENTITY',
            'options': [
                {'option': 'Option 1', 'number': 1, 'votes': 5},
                {'option': 'Option 2', 'number': 2, 'votes': 0},
                {'option': 'Option 3', 'number': 3, 'votes': 3}
            ]
        }, {
            'type': 'IDENTITY',
            'options': [
                {'option': 'Option 1', 'number': 1, 'votes': 2},
                {'option': 'Option 2', 'number': 2, 'votes': 5},
                {'option': 'Option 3', 'number': 3, 'votes': 1}
            ]
        }]

        #El orden debe ser descendente, según el serializer
        expected_result = [{
            'type': 'IDENTITY',
            'options': [
                {'option': 'Option 1', 'number': 1, 'votes': 5,
                 'postproc': 5},
                {'option': 'Option 3', 'number': 3, 'votes': 3,
                 'postproc': 3},
                {'option': 'Option 2', 'number': 2, 'votes': 0,
                 'postproc': 0}
            ]
        }, {
            'type': 'IDENTITY',
            'options': [
                {'option': 'Option 2', 'number': 2, 'votes': 5,
                 'postproc': 5},
                {'option': 'Option 1', 'number': 1, 'votes': 2,
                 'postproc': 2},
                {'option': 'Option 3', 'number': 3, 'votes': 1,
                 'postproc': 1}
            ]
        }]


        response = self.client.post('/postproc/', data, format='json')
        self.assertEqual(response.status_code, 200)

        values = response.json()
        self.assertEqual(values, expected_result)

    def test_identity_multiple_questions_2(self):
        data = [{
            'type': 'IDENTITY',
            'options': [
                {'option': 'Option 1', 'number': 1, 'votes': 10},
                {'option': 'Option 2', 'number': 2, 'votes': 1},
                {'option': 'Option 3', 'number': 3, 'votes': 2},
                {'option': 'Option 4', 'number': 4, 'votes': 0}
            ]
        }, {
            'type': 'IDENTITY',
            'options': [
                {'option': 'Option 1', 'number': 1, 'votes': 2},
                {'option': 'Option 2', 'number': 2, 'votes': 3},
                {'option': 'Option 3', 'number': 3, 'votes': 1}
            ]
        }]

        #El orden debe ser descendente, según el serializer
        expected_result = [{
            'type': 'IDENTITY',
            'options': [
                {'option': 'Option 1', 'number': 1, 'votes': 10,
                 'postproc': 10},
                {'option': 'Option 3', 'number': 3, 'votes': 2,
                 'postproc': 2},
                {'option': 'Option 2', 'number': 2, 'votes': 1,
                 'postproc': 1},
                {'option': 'Option 4', 'number': 4, 'votes': 0,
                 'postproc': 0}
            ]
        }, {
            'type': 'IDENTITY',
            'options': [
                {'option': 'Option 2', 'number': 2, 'votes': 3,
                 'postproc': 3},
                {'option': 'Option 1', 'number': 1, 'votes': 2,
                 'postproc': 2},
                {'option': 'Option 3', 'number': 3, 'votes': 1,
                 'postproc': 1}
            ]
        }]


        response = self.client.post('/postproc/', data, format='json')
        self.assertEqual(response.status_code, 200)

        values = response.json()
        self.assertEqual(values, expected_result)


    def test_hondt(self):
        data = [{
            'type': 'HONDT',
            'options': [
                {'option': 'Option 1', 'number': 1, 'points': 10, 'votes_masc': 0, 'votes_fem': 0, 'votes': 500000},
                {'option': 'Option 2', 'number': 2, 'points': 10, 'votes_masc': 0, 'votes_fem': 0, 'votes': 420000},
                {'option': 'Option 3', 'number': 3, 'points': 10, 'votes_masc': 0, 'votes_fem': 0, 'votes': 310000},
                {'option': 'Option 4', 'number': 4, 'points': 10, 'votes_masc': 0, 'votes_fem': 0, 'votes': 200000},
                {'option': 'Option 5', 'number': 5, 'points': 10, 'votes_masc': 0, 'votes_fem': 0, 'votes': 180000},
                {'option': 'Option 6', 'number': 6, 'points': 10, 'votes_masc': 0, 'votes_fem': 0, 'votes': 170000},
            ]
        }]

        expected_result = [{
            'type': 'HONDT',
            'options': [
                {'option': 'Option 1', 'number': 1, 'points': 10, 'votes_masc': 0, 'votes_fem': 0, 'votes': 500000,
                 'postproc': 3},
                {'option': 'Option 2', 'number': 2, 'points': 10, 'votes_masc': 0, 'votes_fem': 0, 'votes': 420000,
                 'postproc': 2},
                {'option': 'Option 3', 'number': 3, 'points': 10, 'votes_masc': 0, 'votes_fem': 0, 'votes': 310000,
                 'postproc': 2},
                {'option': 'Option 4', 'number': 4, 'points': 10, 'votes_masc': 0, 'votes_fem': 0, 'votes': 200000,
                 'postproc': 1},
                {'option': 'Option 5', 'number': 5, 'points': 10, 'votes_masc': 0, 'votes_fem': 0, 'votes': 180000,
                 'postproc': 1},
                {'option': 'Option 6', 'number': 6, 'points': 10, 'votes_masc': 0, 'votes_fem': 0, 'votes': 170000,
                 'postproc': 1},
            ]
        }]

        response = self.client.post('/postproc/', data, format='json')
        self.assertEqual(response.status_code, 200)

        values = response.json()
        self.assertEqual(values, expected_result)


    def test_hondt2(self):
        data = [{
            'type': 'HONDT',
            'options': [
                {'option': 'Option 1', 'number': 1, 'points': 8, 'votes_masc': 0, 'votes_fem': 0, 'votes': 500000},
                {'option': 'Option 2', 'number': 2, 'points': 8, 'votes_masc': 0, 'votes_fem': 0, 'votes': 420000},
                {'option': 'Option 3', 'number': 3, 'points': 8, 'votes_masc': 0, 'votes_fem': 0, 'votes': 310000},
                {'option': 'Option 4', 'number': 4, 'points': 8, 'votes_masc': 0, 'votes_fem': 0, 'votes': 180000},
                {'option': 'Option 5', 'number': 5, 'points': 8, 'votes_masc': 0, 'votes_fem': 0, 'votes': 20000},
            ]
        }]

        expected_result = [{
            'type': 'HONDT',
            'options': [
                {'option': 'Option 1', 'number': 1, 'points': 8, 'votes_masc': 0, 'votes_fem': 0, 'votes': 500000,
                 'postproc': 3},
                {'option': 'Option 2', 'number': 2, 'points': 8, 'votes_masc': 0, 'votes_fem': 0, 'votes': 420000,
                 'postproc': 2},
                {'option': 'Option 3', 'number': 3, 'points': 8, 'votes_masc': 0, 'votes_fem': 0, 'votes': 310000,
                 'postproc': 2},
                {'option': 'Option 4', 'number': 4, 'points': 8, 'votes_masc': 0, 'votes_fem': 0, 'votes': 180000,
                 'postproc': 1},
                {'option': 'Option 5', 'number': 5, 'points': 8, 'votes_masc': 0, 'votes_fem': 0, 'votes': 20000,
                 'postproc': 0},
            ]
        }]

        response = self.client.post('/postproc/', data, format='json')
        self.assertEqual(response.status_code, 200)

        values = response.json()
        self.assertEqual(values, expected_result)


    def test_hondt_without_points(self):
        data = [{
            'type': 'HONDT',
            'options': [
                {'option': 'Option 1', 'number': 1, 'points': 0, 'votes_masc': 0, 'votes_fem': 0, 'votes': 500000},
                {'option': 'Option 2', 'number': 2, 'points': 0, 'votes_masc': 0, 'votes_fem': 0, 'votes': 420000},
                {'option': 'Option 3', 'number': 3, 'points': 0, 'votes_masc': 0, 'votes_fem': 0, 'votes': 310000},
                {'option': 'Option 4', 'number': 4, 'points': 0, 'votes_masc': 0, 'votes_fem': 0, 'votes': 180000},
                {'option': 'Option 5', 'number': 5, 'points': 0, 'votes_masc': 0, 'votes_fem': 0, 'votes': 20000},
            ]
        }]

        expected_result = [{
            'type': 'HONDT',
            'options': [
                {'option': 'Option 1', 'number': 1, 'points': 0, 'votes_masc': 0, 'votes_fem': 0, 'votes': 500000,
                 'postproc': 0},
                {'option': 'Option 2', 'number': 2, 'points': 0, 'votes_masc': 0, 'votes_fem': 0, 'votes': 420000,
                 'postproc': 0},
                {'option': 'Option 3', 'number': 3, 'points': 0, 'votes_masc': 0, 'votes_fem': 0, 'votes': 310000,
                 'postproc': 0},
                {'option': 'Option 4', 'number': 4, 'points': 0, 'votes_masc': 0, 'votes_fem': 0, 'votes': 180000,
                 'postproc': 0},
                {'option': 'Option 5', 'number': 5, 'points': 0, 'votes_masc': 0, 'votes_fem': 0, 'votes': 20000,
                 'postproc': 0},
            ]
        }]

        response = self.client.post('/postproc/', data, format='json')
        self.assertEqual(response.status_code, 200)

        values = response.json()
        self.assertEqual(values, expected_result)


    def test_hondt_without_votes(self):
        data = [{
            'type': 'HONDT',
            'options': [
                {'option': 'Option 1', 'number': 1, 'points': 8, 'votes_masc': 0, 'votes_fem': 0, 'votes': 0},
                {'option': 'Option 2', 'number': 2, 'points': 8, 'votes_masc': 0, 'votes_fem': 0, 'votes': 0},
                {'option': 'Option 3', 'number': 3, 'points': 8, 'votes_masc': 0, 'votes_fem': 0, 'votes': 0},
                {'option': 'Option 4', 'number': 4, 'points': 8, 'votes_masc': 0, 'votes_fem': 0, 'votes': 0},
                {'option': 'Option 5', 'number': 5, 'points': 8, 'votes_masc': 0, 'votes_fem': 0, 'votes': 0},
            ]
        }]

        expected_result = [{
            'type': 'HONDT',
            'options': [
                {'option': 'Option 1', 'number': 1, 'points': 8, 'votes_masc': 0, 'votes_fem': 0, 'votes': 0,
                 'postproc': 0},
                {'option': 'Option 2', 'number': 2, 'points': 8, 'votes_masc': 0, 'votes_fem': 0, 'votes': 0,
                 'postproc': 0},
                {'option': 'Option 3', 'number': 3, 'points': 8, 'votes_masc': 0, 'votes_fem': 0, 'votes': 0,
                 'postproc': 0},
                {'option': 'Option 4', 'number': 4, 'points': 8, 'votes_masc': 0, 'votes_fem': 0, 'votes': 0,
                 'postproc': 0},
                {'option': 'Option 5', 'number': 5, 'points': 8, 'votes_masc': 0, 'votes_fem': 0, 'votes': 0,
                 'postproc': 0},
            ]
        }]

        response = self.client.post('/postproc/', data, format='json')
        self.assertEqual(response.status_code, 200)

        values = response.json()
        self.assertEqual(values, expected_result)


    def test_hondt_without_option_attribute(self):
        with self.assertRaises(KeyError):
            data = [{
                'type': 'HONDT'
            }]

            response = self.client.post('/postproc/', data, format='json')
            

    def test_hondt_without_options(self):
        with self.assertRaises(Exception):
            data = [{
                'type': 'HONDT',
                'options': []
            }]

            response = self.client.post('/postproc/', data, format='json')

    
    def test_sainte_lague(self):
        data = [{
            'type': 'SAINTE_LAGUE',
            'options': [
                {'option': 'Option 1', 'number': 1, 'points': 8, 'votes_masc': 0, 'votes_fem': 0, 'votes': 500000},
                {'option': 'Option 2', 'number': 2, 'points': 8, 'votes_masc': 0, 'votes_fem': 0, 'votes': 420000},
                {'option': 'Option 3', 'number': 3, 'points': 8, 'votes_masc': 0, 'votes_fem': 0, 'votes': 310000},
                {'option': 'Option 4', 'number': 4, 'points': 8, 'votes_masc': 0, 'votes_fem': 0, 'votes': 180000},
                {'option': 'Option 5', 'number': 5, 'points': 8, 'votes_masc': 0, 'votes_fem': 0, 'votes': 20000},
            ]
        }]

        expected_result = [{
            'type': 'SAINTE_LAGUE',
            'options': [
                {'option': 'Option 1', 'number': 1, 'points': 8, 'votes_masc': 0, 'votes_fem': 0, 'votes': 500000,
                 'postproc': 3},
                {'option': 'Option 2', 'number': 2, 'points': 8, 'votes_masc': 0, 'votes_fem': 0, 'votes': 420000,
                 'postproc': 2},
                {'option': 'Option 3', 'number': 3, 'points': 8, 'votes_masc': 0, 'votes_fem': 0, 'votes': 310000,
                 'postproc': 2},
                {'option': 'Option 4', 'number': 4, 'points': 8, 'votes_masc': 0, 'votes_fem': 0, 'votes': 180000,
                 'postproc': 1},
                {'option': 'Option 5', 'number': 5, 'points': 8, 'votes_masc': 0, 'votes_fem': 0, 'votes': 20000,
                 'postproc': 0},
            ]
        }]

        response = self.client.post('/postproc/', data, format='json')
        self.assertEqual(response.status_code, 200)

        values = response.json()
        self.assertEqual(values, expected_result)


    def test_sainte_lague2(self):
        data = [{
            'type': 'SAINTE_LAGUE',
            'options': [
                {'option': 'Option 1', 'number': 1, 'points': 10, 'votes_masc': 0, 'votes_fem': 0, 'votes': 500000},
                {'option': 'Option 2', 'number': 2, 'points': 10, 'votes_masc': 0, 'votes_fem': 0, 'votes': 420000},
                {'option': 'Option 3', 'number': 3, 'points': 10, 'votes_masc': 0, 'votes_fem': 0, 'votes': 310000},
                {'option': 'Option 4', 'number': 4, 'points': 10, 'votes_masc': 0, 'votes_fem': 0, 'votes': 200000},
                {'option': 'Option 5', 'number': 5, 'points': 10, 'votes_masc': 0, 'votes_fem': 0, 'votes': 180000},
                {'option': 'Option 6', 'number': 6, 'points': 10, 'votes_masc': 0, 'votes_fem': 0, 'votes': 170000},
            ]
        }]

        expected_result = [{
            'type': 'SAINTE_LAGUE',
            'options': [
                {'option': 'Option 1', 'number': 1, 'points': 10, 'votes_masc': 0, 'votes_fem': 0, 'votes': 500000,
                 'postproc': 3},
                {'option': 'Option 2', 'number': 2, 'points': 10, 'votes_masc': 0, 'votes_fem': 0, 'votes': 420000,
                 'postproc': 2},
                {'option': 'Option 3', 'number': 3, 'points': 10, 'votes_masc': 0, 'votes_fem': 0, 'votes': 310000,
                 'postproc': 2},
                {'option': 'Option 4', 'number': 4, 'points': 10, 'votes_masc': 0, 'votes_fem': 0, 'votes': 200000,
                 'postproc': 1},
                {'option': 'Option 5', 'number': 5, 'points': 10, 'votes_masc': 0, 'votes_fem': 0, 'votes': 180000,
                 'postproc': 1},
                {'option': 'Option 6', 'number': 6, 'points': 10, 'votes_masc': 0, 'votes_fem': 0, 'votes': 170000,
                 'postproc': 1},
            ]
        }]

        response = self.client.post('/postproc/', data, format='json')
        self.assertEqual(response.status_code, 200)

        values = response.json()
        self.assertEqual(values, expected_result)

        