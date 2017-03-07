from django.conf.urls import url

from mgmt import views

urlpatterns = [
    url(r'^$', views.auth, name='auth'),
    url(r'^new$', views.authcreate, name='authcreate'),
    url(r'^(?P<address>(\w|-)+)$', views.authdetail, name='authdetail'),
]
