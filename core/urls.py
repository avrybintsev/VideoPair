from django.conf.urls import patterns, url

urlpatterns = patterns('core.views',
    url(r'^$', 'index'),
    url(r'^ask', 'ask'),
    url(r'^arp', 'arp')
)