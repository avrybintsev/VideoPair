from django.conf.urls import patterns, url

urlpatterns = patterns('core.views',
    url(r'^$', 'index'),
    url(r'^ask', 'ask'),
    url(r'^inv', 'invalidate'),
    url(r'^cp/gen/(?P<number>\d{1,4})', 'generate'),
    url(r'^cp/loader', 'loader'),
    url(r'^cp/stats', 'csv'),
    url(r'^cp', 'cp'),
)