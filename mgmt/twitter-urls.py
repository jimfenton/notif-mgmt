from django.conf.urls import patterns, url

from mgmt import views

urlpatterns = patterns('',
    url(r'^$', views.twitter, name='twitter'),
    url(r'^/$', views.twitter, name='twitter'),
    url(r'^/new$', views.twittercreate, name='twittercreate'),
    url(r'^/(?P<address>(\w|-)+)$', views.twitterdetail, name='twitterdetail'),
)
