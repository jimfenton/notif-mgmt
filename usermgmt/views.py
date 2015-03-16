from django import forms
from django.contrib.auth.decorators import login_required
from django.db import models
from django.forms import ModelForm, Textarea
from django.forms.models import modelformset_factory
from django.http import HttpResponse, HttpResponseRedirect
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.template import RequestContext, loader
from django.utils import timezone
from usermgmt.models import Authorization, Priority, Notification, Userext, Method, Rule
import uuid

class SettingsForm(ModelForm):
    class Meta:
        model = Userext
        fields = ['email_username', 'email_server', 'email_port', 'email_authentication', 'email_security', 'twilio_sid', 'twilio_token']

class MethodForm(ModelForm):
    class Meta:
        model = Method
        fields = ['active', 'name', 'type', 'address', 'preamble',]
                

@login_required
def auth(request):
    authorization_list = Authorization.objects.filter(user=request.user, deleted=False).order_by('description')
    template = loader.get_template('usermgmt/auth.html')
    context = RequestContext(request, {
        'authorization_list': authorization_list, 'priority_choices': Priority.PRIORITY_CHOICES
        })
    return HttpResponse(template.render(context))

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
        return render(request, 'usermgmt/authdetail.html', {
            'authorization': authorization,
            'priority_choices': Priority.PRIORITY_CHOICES })

@login_required
def authupdate(request, address):
    a = get_object_or_404(Authorization, address=address)
    try:
        name = request.POST['description']
        domain = request.POST['domain']
        maxpri = request.POST['maxpri']
        if 'active' in request.POST:
            active = True
        else:
            active = False
# TODO: This render has problems, doesn't work.
    except (KeyError):
        return render(request,'usermgmt/authdetail.html', {
            'authorization': a,
            'priority_choices': Authorization.PRIORITY_CHOICES,
            'errormessage': "Something went wrong...",
            })
    else:
        a.description = name
        a.domain = domain
        a.maxpri = maxpri
        a.active = active
        if 'Delete' in request.POST:
            a.deleted = True
        a.save()
        if a.deleted:
            return None
        else:
            return a

@login_required
def authnew(request):
    if (request.method == "POST"):
        authorization = authcreate(request)
        return HttpResponseRedirect(authorization.address)
    return render(request, 'usermgmt/authnew.html', {
        'priority_choices': Priority.PRIORITY_CHOICES })

@login_required
def authcreate(request):
    try:
        name = request.POST['description']
        domain = request.POST['domain']
        maxpri = request.POST['maxpri']
        if 'active' in request.POST:
            active = True
        else:
            active = False
# TODO: This render has problems, doesn't work.
    except (KeyError):
        return render(request,'usermgmt/authdetail.html', {
            'authorization': Null,
            'priority_choices': Authorization.PRIORITY_CHOICES,
            'errormessage': "Something went wrong...",
            })
    else:
        a = Authorization(user=request.user,
                          address=str(uuid.uuid4()),
                          domain=domain,
                          description=name,
                          maxpri=maxpri,
                          active=active)
        a.save()
        return a

@login_required
def notif(request):
    notification_list = Notification.objects.exclude(read=True).order_by('priority')
    # above will add .filter(username=request.user.username)
    template = loader.get_template('usermgmt/notif.html')
    context = RequestContext(request, {
        'notification_list': notification_list,
        'priority_choices': Priority.PRIORITY_CHOICES
        })
    return HttpResponse(template.render(context))

@login_required
def notifall(request):
    notification_list = Notification.objects.order_by('priority')
    # above will add .filter(username=request.user.username)
    template = loader.get_template('usermgmt/notifall.html')
    context = RequestContext(request, {
        'notification_list': notification_list,
        'priority_choices': Priority.PRIORITY_CHOICES
        })
    return HttpResponse(template.render(context))

@login_required
def notifdetail(request, notID):
    
    try:
        notification = Notification.objects.get(notID=notID)
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
        return render(request, 'usermgmt/notifdetail.html', {
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
            settings.email_authentication = form.cleaned_data['email_authentication']
            settings.email_security = form.cleaned_data['email_security']
            settings.twilio_sid = form.cleaned_data['twilio_sid']
            settings.twilio_token = form.cleaned_data['twilio_token']
            settings.save()
            return HttpResponseRedirect("/settings")

    form = SettingsForm(instance=settings)
    return render(request, 'usermgmt/settings.html', { 'form': form, 'settings': settings })

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

    return render(request, 'usermgmt/methods.html', { 'formset': formset })

@login_required
def rules(request):
    RuleFormSet = modelformset_factory(Rule, extra=1, can_delete = True)
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
                    r.category = form.cleaned_data['category']
                    if r.category == '':
                        r.category = 0
                    r.method = form.cleaned_data['method']
                    r.save()
            return HttpResponseRedirect("rules")

    else:
        formset = RuleFormSet(queryset=Rule.objects.filter(user=request.user))

    return render(request, 'usermgmt/rules.html', { 'formset': formset })
