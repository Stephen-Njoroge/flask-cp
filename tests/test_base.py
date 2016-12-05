import json
import unittest
from app import app, db


class TestSetup(unittest.TestCase):
    '''Base test class to hold configuration for tests'''

    def setUp(self):
        '''Create a flask test client'''

        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
        self.app = app.test_client()
        db.create_all()
        credentials = {'username': 'Steve', 'password': 'python'}
        self.app.post('/auth/register', data=json.dumps(credentials),
                      content_type='application/json')

        response = self.app.post('/auth/login',
                                 data=json.dumps(credentials),
                                 content_type='application/json')
        token = json.loads(response.get_data().decode())['token']
        self.headers = {'Authorization': token}

    def tearDown(self):
        db.session.remove()
        db.drop_all()
