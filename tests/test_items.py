import json
import unittest

from test_base import TestSetup


class TestBucketListItemPost(TestSetup):

    # Endpoint: /bucketlists/<int:bucketlist_id>/items/ -> POST
    def test_create_item_without_a_name(self):
        bucketlist_data = {
            'name': 'Test Bucket List'
        }
        response = self.app.post('/bucketlists/',
                                 data=json.dumps(bucketlist_data),
                                 content_type='application/json',
                                 headers=self.headers)
        self.assertEqual(str(
            json.loads(response.get_data())['bucketlist']), 'Test Bucket List')

        item_data = {
            'name': None
        }
        response = self.app.post('/bucketlists/1/items/',
                                 data=json.dumps(item_data),
                                 content_type='application/json',
                                 headers=self.headers)
        self.assertEqual(response.status_code, 400)

    def test_create_item_succesfully(self):
        bucketlist_data = {
            'name': 'Test Bucket List'
        }
        response = self.app.post('/bucketlists/',
                                 data=json.dumps(bucketlist_data),
                                 content_type='application/json',
                                 headers=self.headers)
        self.assertEqual(str(
            json.loads(response.get_data())['bucketlist']), 'Test Bucket List')

        item_data = {
            'name': 'Test Item'
        }
        response = self.app.post('/bucketlists/1/items/',
                                 data=json.dumps(item_data),
                                 content_type='application/json',
                                 headers=self.headers)
        print str(json.loads(
            response.get_data())['bucketlist'][0]['items'][0]['name'])
        self.assertEqual(str(json.loads(
            response.get_data())[
            'bucketlist'][0]['items'][0]['name']), 'Test Item')
        self.assertEqual(response.status_code, 201)


class TestBucketListItemPut(TestSetup):

    # Endpoint: /bucketlists/<int:bucketlist_id>/items/<int:item_id> -> PUT
    def test_update_item_without_providing_name(self):
        bucketlist_data = {
            'name': 'Test Bucket List'
        }
        response = self.app.post('/bucketlists/',
                                 data=json.dumps(bucketlist_data),
                                 content_type='application/json',
                                 headers=self.headers)
        self.assertEqual(str(json.loads(response.get_data())['bucketlist']),
                         'Test Bucket List')
        item_data = {
            'name': 'Test Item'
        }
        response = self.app.post('/bucketlists/1/items/',
                                 data=json.dumps(item_data),
                                 content_type='application/json',
                                 headers=self.headers)
        self.assertEqual(str(json.loads(
            response.get_data())[
            'bucketlist'][0]['items'][0]['name']), 'Test Item')
        response = self.app.post('/bucketlists/1/items/',
                                 data=json.dumps(item_data),
                                 content_type='application/json',
                                 headers=self.headers)
        item_data = {'name': None}
        response = self.app.put('/bucketlists/1/items/1',
                                data=json.dumps(item_data),
                                content_type='application/json',
                                headers=self.headers)
        self.assertEqual(response.status_code, 400)

    def test_try_invalid_done_value(self):
        bucketlist_data = {
            'name': 'Test Bucket List'
        }
        response = self.app.post('/bucketlists/',
                                 data=json.dumps(bucketlist_data),
                                 content_type='application/json',
                                 headers=self.headers)
        self.assertEqual(str(json.loads(response.get_data())['bucketlist']),
                         'Test Bucket List')
        item_data = {
            'name': 'Test Item'
        }
        response = self.app.post('/bucketlists/1/items/',
                                 data=json.dumps(item_data),
                                 content_type='application/json',
                                 headers=self.headers)
        self.assertEqual(str(json.loads(
            response.get_data())[
            'bucketlist'][0]['items'][0]['name']), 'Test Item')
        response = self.app.post('/bucketlists/1/items/',
                                 data=json.dumps(item_data),
                                 content_type='application/json',
                                 headers=self.headers)
        item_data = {'name': 'Fluke', 'done': "What?"}
        response = self.app.put('/bucketlists/1/items/1',
                                data=json.dumps(item_data),
                                content_type='application/json',
                                headers=self.headers)
        self.assertEqual(response.status_code, 400)

    def test_successfully_update_item(self):
        bucketlist_data = {
            'name': 'Test Bucket List'
        }
        response = self.app.post('/bucketlists/',
                                 data=json.dumps(bucketlist_data),
                                 content_type='application/json',
                                 headers=self.headers)
        self.assertEqual(str(json.loads(response.get_data())['bucketlist']),
                         'Test Bucket List')
        item_data = {
            'name': 'Test Item'
        }
        response = self.app.post('/bucketlists/1/items/',
                                 data=json.dumps(item_data),
                                 content_type='application/json',
                                 headers=self.headers)
        self.assertEqual(str(json.loads(
            response.get_data())[
            'bucketlist'][0]['items'][0]['name']), 'Test Item')
        response = self.app.post('/bucketlists/1/items/',
                                 data=json.dumps(item_data),
                                 content_type='application/json',
                                 headers=self.headers)
        item_data = {'name': 'Correct', 'done': True}
        response = self.app.put('/bucketlists/1/items/1',
                                data=json.dumps(item_data),
                                content_type='application/json',
                                headers=self.headers)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(str(json.loads(
            response.get_data())[
            'bucketlist'][0]['items'][0]['name']), 'Correct')
        self.assertEqual(str(json.loads(
            response.get_data())[
            'bucketlist'][0]['items'][0]['done']), 'True')


class TestBucketListItemDelete(TestSetup):

    # Endpoint: /bucketlists/<int:bucketlist_id>/items/<int:item_id> -> DELETE
    def test_delete_from_unathorized_or_nonexistent_bucketlist(self):
        response = self.app.delete('/bucketlists/1/items/1',
                                   content_type='application/json',
                                   headers=self.headers)
        self.assertEqual(response.status_code, 404)

    def test_delete_nonexistent_item(self):
        bucketlist_data = {
            'name': 'Test Bucket List'
        }
        response = self.app.post('/bucketlists/',
                                 data=json.dumps(bucketlist_data),
                                 content_type='application/json',
                                 headers=self.headers)
        self.assertEqual(str(json.loads(response.get_data())['bucketlist']),
                         'Test Bucket List')
        response = self.app.delete('/bucketlists/1/items/1',
                                   content_type='application/json',
                                   headers=self.headers)
        self.assertEqual(response.status_code, 404)

    # @unittest.skip("Fail")
    def test_successful_item_deletion(self):
        bucketlist_data = {
            'name': 'Test Bucket List'
        }
        response = self.app.post('/bucketlists/',
                                 data=json.dumps(bucketlist_data),
                                 content_type='application/json',
                                 headers=self.headers)
        self.assertEqual(str(
            json.loads(response.get_data())['bucketlist']), 'Test Bucket List')

        item_data = {
            'name': 'Test Item'
        }
        response = self.app.post('/bucketlists/1/items/',
                                 data=json.dumps(item_data),
                                 content_type='application/json',
                                 headers=self.headers)
        print str(json.loads(
            response.get_data())['bucketlist'][0]['items'][0]['name'])
        self.assertEqual(str(json.loads(
            response.get_data())[
            'bucketlist'][0]['items'][0]['name']), 'Test Item')
        self.assertEqual(response.status_code, 201)
        response = self.app.delete('/bucketlists/1/items/1',
                                   content_type='application/json',
                                   headers=self.headers)
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
