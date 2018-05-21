# views.py - Django views for notification management web interface
#
# Copyright (c) 2014, 2015, 2017 Jim Fenton
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.contrib.auth import logout
from django.core.exceptions import SuspiciousOperation
from django.db import models
from django.forms import ModelForm, Textarea
from django.forms.models import modelformset_factory
from django.http import HttpResponse, HttpResponseRedirect
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.template import loader
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from mgmt.models import Authorization, Priority, Notification, Userext, Method, Rule, Site
from twitter.models import Twitter
import uuid
import datetime

# TODO: Need a much better place to specify this!
NOTIF_HOST = "altmode.net:5342"

class SettingsForm(ModelForm):
    class Meta:
        model = Userext
        widgets = {
            'twilio_token': forms.PasswordInput(render_value=True),
            'twitter_api_secret': forms.PasswordInput(render_value=True),
            }
        fields = ['email_username', 'email_server', 'email_port', 'email_authentication', 'email_security', 'twilio_sid', 'twilio_token', 'twilio_from', 'twitter_access_token', 'twitter_access_token_secret']

class SiteForm(ModelForm):
    class Meta:
        model = Site
        widgets = {
            'twilio_token': forms.PasswordInput(render_value=True),
            'twitter_consumer_secret': forms.PasswordInput(render_value=True),
            }
        fields = ['twilio_sid', 'twilio_token', 'twilio_from', 'twitter_consumer_key', 'twitter_consumer_secret']

class MethodForm(ModelForm):
    class Meta:
        model = Method
        fields = ['active', 'name', 'type', 'address', 'preamble',]
                

@login_required
def auth(request):
    authorization_list = Authorization.objects.filter(user=request.user, deleted=False).order_by('description')
    template = loader.get_template('mgmt/auth.html')
    return HttpResponse(template.render({
        'page': 'auth',
        'authorization_list': authorization_list,
        'priority_choices': Priority.PRIORITY_CHOICES
        }, request))

@login_required
def authdetail(request, address):
    try:
        authorization = Authorization.objects.get(address=address)
    except Authorization.DoesNotExist:
        raise Http404
    else:
        if (request.method == "POST"):
            authorization = authupdate(request, address)
            if (authorization == None):       #Means authorization was deleted
                return HttpResponseRedirect("/auth")
            return HttpResponseRedirect(authorization.address)
        return render(request, 'mgmt/authdetail.html', {
            'authorization': authorization,
            'priority_choices': Priority.PRIORITY_CHOICES })

@login_required
def authupdate(request, address):
    a = get_object_or_404(Authorization, address=address)
    if 'active' in request.POST:
        a.active = True
    else:
        a.active = False
    if 'Delete' in request.POST:
        a.deleted = True
    else:
        a.description = request.POST['description']
        a.maxpri = request.POST['maxpri']

    a.save()
    if a.deleted:
        return None
    else:
        return a

@login_required
@csrf_exempt
def authorize(request):
    name = ""
    domain = ""
    maxpri = 3
    redirect = ""

    if (request.method == "POST"):
        if "name" in request.POST:
            name = request.POST['name']
        if "maxpri" in request.POST:
            maxpri = request.POST['maxpri']
        if "domain" not in request.POST:
            raise SuspiciousOperation
        domain = request.POST['domain']
        if "redirect" not in request.POST:
            raise SuspiciousOperation
        redirect = request.POST['redirect']

    return render(request,'mgmt/authnew.html', {
            'page': 'auth',
            'name': name,
            'domain': domain,
            'maxpri': int(maxpri),
            'redirect': redirect,
            'priority_choices': Priority.PRIORITY_CHOICES })


@login_required
def authcreate(request):
    try:
        name = request.POST['description']
        domain = request.POST['domain']
        maxpri = request.POST['maxpri']
    except (KeyError):
        raise SuspiciousOperation("Missing POST parameter")
    else:
        if name=="":
            name="[unnamed]"
        a = Authorization(user=request.user,
                          address=str(uuid.uuid4()),
                          domain=domain,
                          description=name,
                          maxpri=maxpri,
                          active=True)
        a.save()
        redirect = ""
        if "redirect" in request.POST:
            redirect = request.POST['redirect']
        if redirect == "":
            return HttpResponseRedirect(a.address)
        return HttpResponseRedirect(request.POST['redirect']+"?addr="+a.address+"@"+NOTIF_HOST+"&maxpri="+maxpri)

def home(request):
    template = loader.get_template('mgmt/home.html')
    return HttpResponse(template.render(request))

def dologout(request):
    logout(request)
    return home(request)
    
@login_required
def notif(request):
    notification_list = Notification.objects.filter(user=request.user, read=False, deleted=False,expires__gte=datetime.datetime.now()).order_by('priority','-origtime')
    # above will add .filter(username=request.user.username)
    template = loader.get_template('mgmt/notif.html')
    return HttpResponse(template.render({
        'page': 'notif',
        'notification_list': notification_list,
        'priority_choices': Priority.PRIORITY_CHOICES
        }, request))

@login_required
def notifall(request):
    notification_list = Notification.objects.filter(user=request.user).order_by('priority','-origtime')
    # above will add .filter(username=request.user.username)
    template = loader.get_template('mgmt/notifall.html')
    return HttpResponse(template.render({
        'page': 'notif',
        'notification_list': notification_list,
        'priority_choices': Priority.PRIORITY_CHOICES
        }, request))

@login_required
def notifdetail(request, notID):
    
    try:
        notification = Notification.objects.get(notid=notID)
        # Need to make sure only this user can get notifs
    except Notification.DoesNotExist:
        raise Http404
    else:
        if (request.method == "POST"):
            if 'Unread' in request.POST:
                notification.read = False
                notification.save()
            if 'Delete' in request.POST:
                notification.deleted = True
                notification.save()
            return HttpResponseRedirect("/notif")
        notification.read = True
        notification.save()
        return render(request, 'mgmt/notifdetail.html', {
            'page': '',
            'notification': notification,
            'priority_choices': Priority.PRIORITY_CHOICES })

@login_required
def settings(request):
    try:
        settings = Userext.objects.get(user=request.user)
    except Userext.DoesNotExist:
# Create a user settings record with default values
        settings = Userext(user=request.user)
        settings.save()

    else:
        if (request.method == "POST"):

            form = SettingsForm(request.POST)
            if form.is_valid():
                settings.email_username = form.cleaned_data['email_username']
                settings.email_server = form.cleaned_data['email_server']
                settings.email_port = form.cleaned_data['email_port']
                settings.twilio_sid = form.cleaned_data['twilio_sid']
                settings.twilio_token = form.cleaned_data['twilio_token']
                settings.twilio_from = form.cleaned_data['twilio_from']
                settings.email_authentication = form.cleaned_data['email_authentication']
                settings.email_security = form.cleaned_data['email_security']
                settings.twitter_access_token = form.cleaned_data['twitter_access_token']
                settings.twitter_access_token_secret = form.cleaned_data['twitter_access_token_secret']
                settings.save()
            return HttpResponseRedirect("/settings")

    form = SettingsForm(instance=settings)
    return render(request, 'mgmt/settings.html', { 'page': 'settings', 'form': form, 'settings': settings })

@login_required
@permission_required('user.is_staff', raise_exception=True)
def sitesettings(request):
    try:
        settings = Site.objects.get(site_id = 1)
    except Site.DoesNotExist:
# Create a site settings record. Should only happen at first startup
        settings = Site()
        settings.save()


    else:
        if (request.method == "POST"):

            form = SiteForm(request.POST)
            if form.is_valid():
                settings.twilio_sid = form.cleaned_data['twilio_sid']
                settings.twilio_token = form.cleaned_data['twilio_token']
                settings.twilio_from = form.cleaned_data['twilio_from']
                settings.twitter_consumer_key = form.cleaned_data['twitter_consumer_key']
                settings.twitter_consumer_secret = form.cleaned_data['twitter_consumer_secret']
                settings.save()
            return HttpResponseRedirect("/sitesettings")
            
    form = SiteForm(instance=settings)
    return render(request, 'mgmt/sitesettings.html', { 'page': 'sitesettings', 'form': form })
                


@login_required
def methods(request):
    MethodFormSet = modelformset_factory(Method, extra=1, exclude=('user',), can_delete = True)
    if (request.method == "POST"):
        formset = MethodFormSet(request.POST)
        if formset.is_valid():
            for form in formset:
                if 'id' in form.cleaned_data:
                    m = form.cleaned_data['id']
                    if (m==None):
                        m = Method(user=request.user)
                    m.active = form.cleaned_data['active']
                    m.name = form.cleaned_data['name']
                    m.type = form.cleaned_data['type']
                    m.address = form.cleaned_data['address']
                    if 'preamble' in form.cleaned_data:
                        m.preamble = form.cleaned_data['preamble']
                    else:
                        m.preamble = ""
                    m.save()
            return HttpResponseRedirect("methods")

    else:
        formset = MethodFormSet(queryset=Method.objects.filter(user=request.user))

    return render(request, 'mgmt/methods.html', { 'page': 'methods', 'formset': formset })

@login_required
def rules(request):
    RuleFormSet = modelformset_factory(Rule, extra=1, exclude=('user',), can_delete = True)
    if (request.method == "POST"):
        formset = RuleFormSet(request.POST, initial=[
            {'user': request.user,}])
        if formset.is_valid():
            for form in formset:
                if 'id' in form.cleaned_data:
                    r = form.cleaned_data['id']
                    if (r==None):
                        r = Rule(user=request.user)
                    r.active = form.cleaned_data['active']
                    r.priority = form.cleaned_data['priority']
                    if r.priority == '':
                        r.priority = 0
                    r.domain = form.cleaned_data['domain']
                    r.method = form.cleaned_data['method']
                    r.save()
            return HttpResponseRedirect("rules")

    else:
        formset = RuleFormSet(queryset=Rule.objects.filter(user=request.user))

    return render(request, 'mgmt/rules.html', { 'page': 'rules', 'formset': formset })

@login_required
def twitter(request):
            
    filter_list = Twitter.objects.filter(user=request.user, deleted=False).order_by('source')
    template = loader.get_template('twitter/twitter.html')
    return HttpResponse(template.render({
        'page': 'twitter',
        'filter_list': filter_list,
        'filter_types': Twitter.CHOICES,
        'priority_choices': Priority.PRIORITY_CHOICES,
        'lifetimes': Twitter.LIFETIMES,
        }, request))

@login_required
def twitterdetail(request, address):
    try:
        filter = Twitter.objects.get(id=address)
    except Twitter.DoesNotExist:
        raise Http404
    else:
        if (request.method == "POST"):
            filter = twitterupdate(request, address)
            if (filter == None):       #Means filter was deleted
                return HttpResponseRedirect("/twitter")
            return HttpResponseRedirect("/twitter/"+address)
        return render(request, 'twitter/detail.html', {
            'filter': filter,
            'filterid': address,
            'type_choices': Twitter.CHOICES,
            'priority_choices': Priority.PRIORITY_CHOICES,
            'lifetimes': Twitter.LIFETIMES})

@login_required
def twitterupdate(request, address):
    filter = get_object_or_404(Twitter, id=address)
    if 'active' in request.POST:
        filter.active = True
    else:
        filter.active = False
    if 'Delete' in request.POST:
        filter.deleted = True
    else:
        filter.type = request.POST['type']
        filter.source = request.POST['source']
        filter.keyword = request.POST['keyword']
        filter.priority = request.POST['priority']
        filter.lifetime = request.POST['lifetime']
        filter.tag = request.POST['tag']

    filter.save()
    if filter.deleted:
        return None
    else:
        return filter


@login_required
def twittercreate(request):
    if (request.method == "POST"):
        try:
            type = request.POST['type']
            source = request.POST['source']
            keyword = request.POST['keyword']
            priority = request.POST['priority']
            lifetime = request.POST['lifetime']
            tag = request.POST['tag']
        except (KeyError):
            raise SuspiciousOperation("Missing POST parameter")
        else:
            filter = Twitter(user=request.user,
                        type = type,
                        source = source,
                        keyword = keyword,
                        priority = priority,
                        lifetime = lifetime,
                        tag = tag)
            if (source == "" and keyword == ""):
                return render(request, 'twitter/new.html', {
                    'filter': filter,
                    'filter_types': Twitter.CHOICES,
                    'priority_choices': Priority.PRIORITY_CHOICES,
                    'lifetimes': Twitter.LIFETIMES,
                    'message': 'Source and keyword cannot both be blank'})

            filter.save()
            return twitter(request)


    filter = Twitter(user=request.user,
                        type = Twitter.TWEET,
                        source = "",
                        keyword = "",
                        priority = Priority.ROUTINE)

    return render(request, 'twitter/new.html', {
        'filter': filter,
        'filter_types': Twitter.CHOICES,
        'priority_choices': Priority.PRIORITY_CHOICES,
        'lifetimes': Twitter.LIFETIMES})
