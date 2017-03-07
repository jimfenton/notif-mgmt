from django.conf.urls import url

from mgmt import views

urlpatterns = [
    url(r'^$', views.notif, name='notif'),
    url(r'^all$', views.notifall, name='notifall'),
    url(r'^all/$', views.notifall, name='notifall'),
    url(r'^(?P<notID>(\w|-)+)$', views.notifdetail, name='notifdetail'),
]
