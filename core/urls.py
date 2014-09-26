from django.conf.urls import patterns, url

urlpatterns = patterns('core.views',
    url(r'^$', 'index'),
    url(r'^ask', 'ask'),
    url(r'^cp', 'cp'),
    url(r'^csv', 'csv'),
    url(r'^gen/(?P<number>\d{1,4})', 'generate')
)