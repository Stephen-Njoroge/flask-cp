import json
import unittest

from test_base import TestSetup


class TestAuthRegister(TestSetup):
    # Endpoint: /auth/register -> POST
    def test_registration_without_credentials(self):
        credentials = {}
        response = self.app.post('/auth/register',
                                 data=json.dumps(credentials),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_registration_without_username(self):
        credentials = {'password': 'pymania'}
        response = self.app.post('/auth/register',
                                 data=json.dumps(credentials),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_registration_without_password(self):
        credentials = {'username': 'hardcode'}
        response = self.app.post('/auth/register',
                                 data=json.dumps(credentials),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_duplicate_user_registration(self):
        credentials = {'username': 'testuser', 'password': 'testpassword'}
        response = self.app.post('/auth/register',
                                 data=json.dumps(credentials),
                                 content_type='application/json')
        credentials = {'username': 'testuser', 'password': 'testpassword'}
        response = self.app.post('/auth/register',
                                 data=json.dumps(credentials),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_successful_user_registration(self):
        credentials = {'username': 'user_one', 'password': 'password_one'}
        response = self.app.post('/auth/register',
                                 data=json.dumps(credentials),
                                 content_type='application/json')
        self.assertEqual(dict(json.loads(response.get_data())),
                         {'Hello': credentials['username']})
        self.assertEqual(response.status_code, 201)


class TestAuthLogin(TestSetup):

    # Endpoint: /auth/login -> POST
    def test_login_without_username_and_password(self):
        credentials = {}
        response = self.app.post('/auth/login',
                                 data=json.dumps(credentials),
                                 content_type='application/json')
        self.assertEqual(dict(json.loads(response.get_data())),
                         {'Error': 'Register To Use Service!'})
        self.assertEqual(response.status_code, 401)

    def test_login_without_username(self):
        credentials = {'password': 'testpassword'}
        response = self.app.post('/auth/login',
                                 data=json.dumps(credentials),
                                 content_type='application/json')
        self.assertEqual(dict(json.loads(response.get_data())),
                         {'Error': 'Register To Use Service!'})
        self.assertEqual(response.status_code, 401)

    def test_login_without_password(self):
        credentials = {'username': 'testuser'}
        response = self.app.post('/auth/login',
                                 data=json.dumps(credentials),
                                 content_type='application/json')
        self.assertEqual(dict(json.loads(response.get_data())),
                         {'Error': 'Register To Use Service!'})
        self.assertEqual(response.status_code, 401)

    def test_login_with_invalid_username(self):
        credentials = {'username': 'testuser1', 'password': 'testpassword'}
        response = self.app.post('/auth/login',
                                 data=json.dumps(credentials),
                                 content_type='application/json')
        self.assertEqual(dict(json.loads(response.get_data())),
                         {'Error': 'Register To Use Service!'})
        self.assertEqual(response.status_code, 401)

    def test_login_with_invalid_password(self):
        credentials = {'username': 'testuser', 'password': 'testpassworddd'}
        response = self.app.post('/auth/login',
                                 data=json.dumps(credentials),
                                 content_type='application/json')
        self.assertEqual(dict(json.loads(response.get_data())),
                         {'Error': 'Register To Use Service!'})
        self.assertEqual(response.status_code, 401)

    def test_successful_user_login(self):
        credentials = {'username': 'user', 'password': 'python'}
        response = self.app.post('/auth/register',
                                 data=json.dumps(credentials),
                                 content_type='application/json')
        self.assertEqual(dict(json.loads(response.get_data())),
                         {'Hello': credentials['username']})
        self.assertEqual(response.status_code, 201)
        credentials = {'username': 'user', 'password': 'python'}
        response = self.app.post('/auth/login',
                                 data=json.dumps(credentials),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(json.loads(response.get_data())['Greetings']),
                         'user')

    def test_invalid_token(self):
        self.headers['Authorization'] = "Token abracadabra"
        response = self.app.get('/bucketlists/',
                                content_type='application/json',
                                headers=self.headers)
        self.assertEqual(response.status_code, 401)


if __name__ == '__main__':
    unittest.main()
