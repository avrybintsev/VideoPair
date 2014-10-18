from django.conf.urls import patterns, url

urlpatterns = patterns('core.views',
    url(r'^(?P<lang>(en|ru))/$', 'index'),
    url(r'^new', 'new'),
    url(r'^inv', 'invalidate'),
    url(r'^ans', 'answer'),
    url(r'^cp/gen/(?P<number>\d{1,4})', 'generate'),
    url(r'^cp/loader', 'loader'),
    url(r'^cp/stats', 'csv'),
    url(r'^cp', 'cp'),
)