from django.conf.urls import url, patterns, include
from .api import DataSetResource, UserResource
from tastypie.api import Api


v1_api = Api(api_name='v1')
v1_api.register(DataSetResource())
v1_api.register(UserResource())


urlpatterns = patterns('alyticsproc.views',
    url(r'^$', 'index', name='index'),
    url(r'^save-test-data$', 'save_testdata', name='save_testdata'),
    url(r'^start-processing/$', 'start_processing', name='start_processing'),

    url(r'api/', include(v1_api.urls)),
)