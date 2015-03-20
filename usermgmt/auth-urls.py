from django.conf.urls import patterns, url

from usermgmt import views

urlpatterns = patterns('',
    url(r'^$', views.auth, name='auth'),
    url(r'^/$', views.auth, name='auth'),
    url(r'^/new$', views.authcreate, name='authcreate'),
    url(r'^/(?P<address>(\w|-)+)$', views.authdetail, name='authdetail'),
)
