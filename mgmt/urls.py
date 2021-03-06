from django.conf.urls import include, url
from django.contrib.auth import views as auth_views
from mgmt import views

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    # Examples:
url(r'^$', views.home, name='home'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', admin.site.urls),
    url('^', include('django.contrib.auth.urls')),
    url(r'^accounts/login/$', auth_views.LoginView.as_view()),
    url(r'^authorize', views.authorize, name='authorize'),
    url(r'^authcfm', views.authcfm, name='authcfm'),
    url(r'^auth/', include('mgmt.auth-urls')),
    url(r'^notif/', include('mgmt.notif-urls')),
    url(r'^settings', views.settings, name='settings'),
    url(r'^sitesettings', views.sitesettings, name='sitesettings'),
    url(r'^methods', views.methods, name='methods'),
    url(r'^rules', views.rules, name='rules'),
    url(r'^logout', views.dologout, name='logout'),
]
