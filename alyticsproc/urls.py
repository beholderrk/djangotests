from django.conf.urls import url, patterns, include

urlpatterns = patterns('alyticsproc.views',
    url(r'^$', 'index', name='index'),
    url(r'^start-processing/$', 'start_processing', name='start_processing'),
)