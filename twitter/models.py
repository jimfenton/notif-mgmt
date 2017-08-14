from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from mgmt.models import Priority

# Create your models here.

class Twitter(models.Model):

    TWEET = 0
    DIRECT = 1
    RETWEET = 2
    MENTION = 3

    CHOICES = (
        (TWEET, 'Tweet'),
        (DIRECT, 'Direct Message'),
        (RETWEET, 'Retweet'),
        (MENTION, 'Mention'),
        )


    user = models.ForeignKey(User, editable=False)
    type = models.IntegerField(choices=CHOICES, blank=True)    
    source = models.CharField(max_length=64, blank=True)
    keyword = models.CharField(max_length=64, blank=True)
    priority = models.IntegerField(choices=Priority.PRIORITY_CHOICES, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    latest = models.DateTimeField(null=True)
    count = models.IntegerField(default=0)
    active = models.BooleanField(default=True)
    deleted = models.BooleanField(default=False)

    class Meta:
        db_table = "twitter"

