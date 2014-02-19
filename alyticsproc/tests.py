from django.core.urlresolvers import reverse
from tastypie.test import ResourceTestCase
from django.contrib.auth.models import User
from .models import DataSet, ExecHistory
from model_mommy import mommy


class DataSetResourceTest(ResourceTestCase):
    def setUp(self):
        super(DataSetResourceTest, self).setUp()

        self.username = 'admin'
        self.password = 'password'
        self.user = User.objects.create_user(self.username, 'admin@example.com', self.password)

        self.post_url = self.get_list_url = '/api/v1/dataset/'
        self.get_detail_url_tmpl = '/api/v1/dataset/%d/'

        self.post_data = {"name": "post dataset", "items": [{"a": 1, "b": 1}]}

        d1 = mommy.make('alyticsproc.Dataset', name='first', user=self.user)
        d2 = mommy.make('alyticsproc.Dataset', name='second', user=self.user)
        d3 = mommy.make('alyticsproc.Dataset', name='third', user=self.user)
        d4 = mommy.make('alyticsproc.Dataset', name='fourth', user=self.user)
        d5 = mommy.make('alyticsproc.Dataset', name='not admin dataset')

        for d in (d1, d2, d3, d4, d5):
            mommy.make('alyticsproc.DataItem', dataset=d)
            mommy.make('alyticsproc.DataItem', dataset=d)

        self.ds_not_user = d5
        self.ds_for_get = d1
        self.detail_url = self.get_detail_url_tmpl % self.ds_for_get.pk

    def get_credentials(self):
        return self.create_basic(username=self.username, password=self.password)

    def test_get_list_unauthorized(self):
        self.assertHttpUnauthorized(self.api_client.get(self.get_list_url, format='json'))

    def test_get_list_json(self):
        resp = self.api_client.get(self.get_list_url, format='json', authentication=self.get_credentials())
        self.assertValidJSONResponse(resp)
        self.assertEqual(len(self.deserialize(resp)['objects']), 4)

        first_dataset = self.deserialize(resp)['objects'][0]
        self.assertEqual(first_dataset['name'], 'first')
        self.assertTrue(isinstance(first_dataset['items'], (list, tuple)))
        self.assertEqual(len(first_dataset['items']), 2)
        self.assertTrue(isinstance(first_dataset['items'][0]['a'], int))
        self.assertTrue(isinstance(first_dataset['items'][0]['b'], int))

    def test_post_list_unauthorized(self):
        self.assertHttpUnauthorized(self.api_client.post(self.post_url, format='json', data=self.post_data))

    def test_post_list(self):
        self.assertEqual(DataSet.objects.filter(user=self.user).count(), 4)
        self.assertHttpCreated(self.api_client.post(self.post_url, format='json', data=self.post_data,
                                                    authentication=self.get_credentials()))
        self.assertEqual(DataSet.objects.filter(user=self.user).count(), 5)
        posted_dataset = DataSet.objects.get(name=self.post_data['name'])
        self.assertEqual(posted_dataset.name, self.post_data['name'])
        self.assertEqual(repr(posted_dataset.dataitem_set.all().values('a', 'b')), repr(self.post_data['items']))

    def test_get_detail_json_unauthorized(self):
        self.assertHttpUnauthorized(self.api_client.get(self.detail_url, format='json'))
        self.assertHttpUnauthorized(self.api_client.get(self.get_detail_url_tmpl % self.ds_not_user.pk, format='json',
                                                        authentication=self.get_credentials()))

    def test_get_detail_json(self):
        resp = self.api_client.get(self.detail_url, format='json', authentication=self.get_credentials())
        self.assertValidJSONResponse(resp)
        obj = self.deserialize(resp)
        self.assertEqual(obj['name'], self.ds_for_get.name)
        self.assertTrue(isinstance(obj['items'], (list, tuple)))
        self.assertEqual(len(obj['items']), 2)
        self.assertEqual(obj['items'][0]['a'], self.ds_for_get.dataitem_set.all()[0].a)
        self.assertEqual(obj['items'][0]['b'], self.ds_for_get.dataitem_set.all()[0].b)

    def test_put_detail_unauthorized(self):
        self.assertHttpUnauthorized(self.api_client.put(self.detail_url, format='json', data={}))
        self.assertHttpUnauthorized(self.api_client.put(self.get_detail_url_tmpl % self.ds_not_user.pk, format='json',
                                                        data={}, authentication=self.get_credentials()))

    def test_put_detail(self):
        # Grab the current data & modify it slightly.
        original_data = self.deserialize(self.api_client.get(self.detail_url, format='json', authentication=self.get_credentials()))
        new_data = original_data.copy()
        new_data['name'] = 'Updated: first'
        new_data['items'][0]['a'] = 1
        new_data['items'][0]['b'] = 1

        count = DataSet.objects.count()
        self.assertHttpAccepted(self.api_client.put(self.detail_url, format='json', data=new_data, authentication=self.get_credentials()))
        # Make sure the count hasn't changed & we did an update.
        self.assertEqual(DataSet.objects.count(), count)
        updated_ds = DataSet.objects.get(pk=self.ds_for_get.pk)
        self.assertEqual(updated_ds.name, new_data['name'])
        self.assertEqual(updated_ds.dataitem_set.all()[0].a, new_data['items'][0]['a'])
        self.assertEqual(updated_ds.dataitem_set.all()[0].b, new_data['items'][0]['b'])

    def test_delete_detail_unauthorized(self):
        self.assertHttpUnauthorized(self.api_client.delete(self.detail_url, format='json'))
        self.assertHttpUnauthorized(self.api_client.delete(self.get_detail_url_tmpl % self.ds_not_user.pk, format='json',
                                                           authentication=self.get_credentials()))

    def test_delete_detail(self):
        count = DataSet.objects.count()
        self.assertHttpAccepted(self.api_client.delete(self.detail_url, format='json', authentication=self.get_credentials()))
        self.assertEqual(DataSet.objects.count(), count - 1)


class ExecHistoryResourceTest(ResourceTestCase):
    def setUp(self):
        super(ExecHistoryResourceTest, self).setUp()

        self.username = 'admin'
        self.password = 'password'
        self.user = User.objects.create_user(self.username, 'admin@example.com', self.password)

        self.list_url = '/api/v1/exechistory/'
        self.detail_url_tmpl = '/api/v1/exechistory/%d/'

        self.user_history = [mommy.make('alyticsproc.ExecHistory', success=True, error=False, dataset__user=self.user) for i in xrange(4)]
        self.not_user_history = [mommy.make('alyticsproc.ExecHistory', success=True, error=False) for i in xrange(4)]
        self.detail_url = self.detail_url_tmpl % self.user_history[0].pk

    def get_credentials(self):
        return self.create_basic(username=self.username, password=self.password)

    def test_get_list_unauthorized(self):
        self.assertHttpUnauthorized(self.api_client.get(self.list_url, format='json'))

    def test_get_list_json(self):
        resp = self.api_client.get(self.list_url, format='json', authentication=self.get_credentials())
        self.assertValidJSONResponse(resp)
        self.assertEqual(len(self.deserialize(resp)['objects']), 4)

        f_resp_history = self.deserialize(resp)['objects'][0]
        self.assertKeys(f_resp_history, ('id', 'success', 'error', 'result', 'resource_uri', 'exception', 'dataset', 'date_modified', 'date_creation'))

    def test_get_detail_json_unauthorized(self):
        self.assertHttpUnauthorized(self.api_client.get(self.detail_url, format='json'))
        self.assertHttpUnauthorized(self.api_client.get(self.detail_url_tmpl % self.not_user_history[0].pk, format='json',
                                                        authentication=self.get_credentials()))

    def test_get_detail_json(self):
        resp = self.api_client.get(self.detail_url, format='json', authentication=self.get_credentials())
        self.assertValidJSONResponse(resp)
        obj = self.deserialize(resp)
        self.assertKeys(obj, ('id', 'success', 'error', 'result', 'resource_uri', 'exception', 'dataset', 'date_modified', 'date_creation'))


