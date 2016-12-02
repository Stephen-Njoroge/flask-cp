import json
import unittest
from test_base import TestSetup


class TestBucketListsPost(TestSetup):

    # Endpoint: /bucketlists/ -> POST
    def test_create_bucket_list_without_authorization(self):
        bucketlist_data = {'name': 'Unauthorized'}
        response = self.app.post('/bucketlists/',
                                 content_type='application/json',
                                 data=json.dumps(bucketlist_data))
        self.assertEqual(response.status_code, 401)

    # Endpoint: /bucketlists/ -> POST
    def test_create_bucket_list(self):
        bucketlist_data = {'name': 'Authorizedd'}
        response = self.app.post('/bucketlists/',
                                 content_type='application/json',
                                 headers=self.headers,
                                 data=json.dumps(bucketlist_data))
        self.assertEqual(response.status_code, 201)
        print str(json.loads(response.get_data()))
        self.assertEqual(str(json.loads(response.get_data())['bucketlist']),
                         'Authorizedd')

    # Endpoint: /bucketlists/ -> POST
    def test_create_bucket_list_with_no_name(self):
        bucketlist_data = {'name': None}
        response = self.app.post('/bucketlists/',
                                 content_type='application/json',
                                 headers=self.headers,
                                 data=json.dumps(bucketlist_data))
        self.assertEqual(response.status_code, 400)


class TestBucketListPut(TestSetup):

    # Endpoint: /bucketlists/<int:bucketlist_id> -> POST
    def test_update_bucket_list_without_name(self):
        bucketlist_data = {
            'name': 'Migwi'
        }
        self.app.post('/bucketlists/',
                      content_type='application/json',
                      headers=self.headers,
                      data=json.dumps(bucketlist_data))
        bucketlist_data2 = {'name': None}
        response = self.app.put('/bucketlists/1',
                                content_type='application/json',
                                headers=self.headers,
                                data=json.dumps(bucketlist_data2))
        self.assertEqual(response.status_code, 400)

    def test_update_bucket_correctly(self):
        bucketlist_data = {
            'name': 'Steve Test'
        }
        response = self.app.post('/bucketlists/',
                                 content_type='application/json',
                                 headers=self.headers,
                                 data=json.dumps(bucketlist_data))
        self.assertEqual(response.status_code, 201)
        bucketlist_data2 = {'name': 'Steve Test Update'}
        response = self.app.put('/bucketlists/1',
                                content_type='application/json',
                                headers=self.headers,
                                data=json.dumps(bucketlist_data2))
        print str(json.loads(
            response.get_data()))
        self.assertEqual(str(json.loads(
            response.get_data())['bucketlist'][0]['name']),
            'Steve Test Update')


class TestBucketListsGet(TestSetup):

    # Endpoint: /bucketlists/ -> GET
    def test_get_non_existent_bucket_list(self):
        response = self.app.get('/bucketlists/',
                                content_type='application/json',
                                headers=self.headers)
        self.assertEqual(response.status_code, 404)

    def test_invalid_limit_value_in_get_url(self):
        response = self.app.get('/bucketlists?limit=sdnkfs',
                                content_type='application/json',
                                headers=self.headers)
        self.assertEqual(str(json.loads(response.get_data())['message']),
                         'Invalid Limit Value')

    # Endpoint: /bucketlists/<int:bucketlist_id> -> GET
    def test_get_with_invalid_url(self):
        response = self.app.get('/bucketlists/nkjn',
                                content_type='application/json',
                                headers=self.headers)
        self.assertEqual(response.status_code, 404)

    def test_get_bucketlist_with_inexistent_bucketlist_id(self):
        response = self.app.get('/bucketlists/1000',
                                content_type='application/json',
                                headers=self.headers)
        self.assertEqual(response.status_code, 404)

    def test_successful_get_bucketlist(self):
        bucketlist_data = {
            'name': 'Steve Test'
        }
        response = self.app.post('/bucketlists/',
                                 data=json.dumps(bucketlist_data),
                                 content_type='application/json',
                                 headers=self.headers)
        print str(json.loads(response.get_data()))
        self.assertEqual(str(json.loads(
            response.get_data())['bucketlist']),
            'Steve Test')


if __name__ == '__main__':
    unittest.main()
