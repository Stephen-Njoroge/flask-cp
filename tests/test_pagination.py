import json
import unittest

from test_base import TestSetup


class TestAuthPagination(TestSetup):
    # Endpoint: bucketlists/?limit=20 -> Get
    def test_invalid_limit_value_in_get_url(self):
        response = self.app.get('/bucketlists/?limit=nil',
                                content_type='application/json',
                                headers=self.headers)
        self.assertEqual(str(json.loads(response.get_data())['message']),
                         'Invalid Limit Value')

    def test_correct_pagination(self):
        bucketlist_data = {'name': 'Authorizedd'}
        response = self.app.post('/bucketlists/',
                                 content_type='application/json',
                                 headers=self.headers,
                                 data=json.dumps(bucketlist_data))
        self.assertEqual(response.status_code, 201)
        print str(json.loads(response.get_data()))
        self.assertEqual(str(json.loads(response.get_data())['bucketlist']),
                         'Authorizedd')
        response = self.app.get('/bucketlists/?limit=30',
                                content_type='application/json',
                                headers=self.headers)
        self.assertEqual(str(json.loads(
            response.get_data())['bucketlists'][0]['name']),
            'Authorizedd')


if __name__ == '__main__':
    unittest.main()
