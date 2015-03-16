from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User

# Create your models here.

# class User(models.Model):
#    username = models.CharField(max_length=32)
#    email = models.CharField(max_length=64)
#    fullname = models.CharField(max_length=64)
#    def __unicode__(self):
#        return self.username

User = get_user_model()

class Userext(models.Model):
    SEC_NONE = 0
    SEC_TLS = 1
    SEC_STARTTLS = 2
    SEC_CHOICES = (
        (SEC_NONE, 'None'),
        (SEC_TLS, 'SSL/TLS'),
        (SEC_STARTTLS, 'STARTTLS'),
        )
    AUTH_NONE = 0
    AUTH_PASS = 1
    AUTH_ENCRPASS = 2
    AUTH_CHOICES = (
        (AUTH_NONE, 'None'),
        (AUTH_PASS, 'Normal password'),
        (AUTH_ENCRPASS, 'Encrypted password'),
        )
    user = models.OneToOneField(User)
    email_username = models.CharField(max_length=64)
    email_server = models.CharField(max_length=64)
    email_port = models.IntegerField(default=587)
    email_authentication = models.IntegerField(choices=AUTH_CHOICES, default=AUTH_ENCRPASS)
    email_security = models.IntegerField(choices=SEC_CHOICES, default=SEC_STARTTLS)
    twilio_sid = models.CharField(max_length=34)
    twilio_token = models.CharField(max_length=34)
    count = models.IntegerField(default=0)
    latest = models.DateTimeField(null=True)
    created = models.DateTimeField(auto_now_add=True)

    

class Priority(models.Model):
    EMERGENCY = 1
    URGENT = 2
    ROUTINE = 3
    INFORMATIONAL = 4
    PRIORITY_CHOICES = (
        (EMERGENCY, 'Emergency'),
        (URGENT, 'Urgent'),
        (ROUTINE, 'Routine'),
        (INFORMATIONAL, 'Informational'),
        )

class Category(models.Model):
    OFFICIAL = 1
    INVITATION = 2
    ADVERTISING = 3
    FINANCIAL = 4
    NEWSLETTER = 5
    ALARM = 6
    ADMINISTRATIVE = 7
    SUPPORT = 8
    SECURITY = 9
    POLL = 10
    VERIFICATION = 11
    CATEGORY_CHOICES = (
        (OFFICIAL, 'Official'),
        (INVITATION, 'Invitation'),
        (ADVERTISING, 'Advertisement'),
        (FINANCIAL, 'Financial'),
        (NEWSLETTER, 'Newsletter'),
        (ALARM, 'Alarm'),
        (ADMINISTRATIVE, 'Administrative'),
        (SUPPORT, 'Support'),
        (SECURITY, 'Security'),
        (POLL, 'Survey'),
        (VERIFICATION, 'Verification'),
        )

class Authorization(models.Model):
    user = models.ForeignKey(User)
    address = models.CharField(max_length=36, unique=True)
    domain = models.CharField(max_length=64)
    description = models.CharField(max_length=64)
    created = models.DateTimeField(auto_now_add=True)
    maxpri = models.IntegerField(choices=Priority.PRIORITY_CHOICES, default=Priority.ROUTINE)
    latest = models.DateTimeField(null=True)
    count = models.IntegerField(default=0)
    active = models.BooleanField(default=True)
    expiration = models.DateTimeField(null=True) # Currently unimplemented, for future use
    deleted = models.BooleanField(default=False)
    
    def __unicode__(self):
        return self.address

class Notification(models.Model):
    username = models.CharField(max_length=30, blank=True) # only temporarily may be blank
    to = models.CharField(max_length=36)
    description = models.CharField(max_length=64)
    origtime = models.DateTimeField()
    priority = models.IntegerField(choices=Priority.PRIORITY_CHOICES, default=Priority.ROUTINE)
    category = models.IntegerField(null=True) # temporarily may be null
    fromdomain = models.CharField(max_length=64)
    expires = models.DateTimeField(null=True) # temporarily may be null (?)
    subject = models.CharField(max_length=80)
    body = models.TextField()
    notID = models.CharField(max_length=36, unique=True)
    recvtime = models.DateTimeField(null=True) #temporarily may be null
    revcount = models.IntegerField(default=0)
    read = models.BooleanField(default=False)
    readtime = models.DateTimeField(null=True) #maybe not so temporary
    source = models.CharField(max_length=80)
    deleted = models.BooleanField(default=False)

    def __unicode__(self):
        if (self.notID == None):
            return "unlabeled notification"
        return self.notID

class Method(models.Model):
    METHOD_EMAIL = 0
    METHOD_SMS = 1
    METHOD_VOICE = 2
    METHOD_CHOICES = (
        (METHOD_EMAIL, 'Email'),
        (METHOD_SMS, 'Text message'),
        (METHOD_VOICE, 'Phone call'),
        )

    user = models.ForeignKey(User)
    active = models.BooleanField(default=False)
    name = models.CharField(max_length=64, unique=True)
    type = models.IntegerField(choices=METHOD_CHOICES)
    address = models.CharField(max_length=32)
    preamble = models.CharField(max_length=64, blank=True, null=True)

    def __unicode__(self):
        return self.name


class Rule(models.Model):

# Parameter choice not currently used - for possible future use.
    PARAMETER_PRIORITYLT = 1
    PARAMETER_PRIORITYLE = 2
    PARAMETER_PRIORITYEQ = 3
    PARAMETER_PRIORITYGE = 4
    PARAMETER_PRIORITYGT = 5
    PARAMETER_DOMAIN = 6
    PARAMETER_CATEGORY = 7
    PARAMETER_CHOICES = (
        (PARAMETER_PRIORITYLT, 'Priority <'),
        (PARAMETER_PRIORITYLE, 'Priority <='),
        (PARAMETER_PRIORITYEQ, 'Priority =='),
        (PARAMETER_PRIORITYGE, 'Priority >='),
        (PARAMETER_PRIORITYGT, 'Priority >'),
        (PARAMETER_DOMAIN, 'Domain'),
        (PARAMETER_CATEGORY, 'Category'),
        )

    user = models.ForeignKey(User, editable=False)
    active = models.BooleanField(default=False)
    priority = models.IntegerField(choices=Priority.PRIORITY_CHOICES, blank=True)
    domain = models.CharField(max_length=64, blank=True)
    category = models.IntegerField(choices=Category.CATEGORY_CHOICES, blank=True)
# TODO: Make sure methods don't bleed from one user to another
    method = models.ForeignKey(Method)
