from django.conf.urls import patterns, include, url
from usermgmt import views

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
url(r'^$', views.home, name='home'),
    # url(r'^notif/', include('notif.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url('^', include('django.contrib.auth.urls')),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login'),
    url(r'^auth', include('usermgmt.auth-urls')),
    url(r'^notif', include('usermgmt.notif-urls')),
    url(r'^settings', views.settings, name='settings'),
    url(r'^methods', views.methods, name='methods'),
    url(r'^rules', views.rules, name='rules'),
    url(r'^logout', views.dologout, name='logout'),
)
