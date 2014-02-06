from django.conf.urls import url, patterns, include

urlpatterns = patterns('alyticsproc.views',
    url(r'^$', 'index', name='index'),
    url(r'^save-test-data$', 'save_testdata', name='save_testdata'),
    url(r'^start-processing/$', 'start_processing', name='start_processing'),
)