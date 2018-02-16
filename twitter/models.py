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

    LIFE_HOUR = 60
    LIFE_12H = 720
    LIFE_DAY = 1440
    LIFE_WEEK = 10080
    LIFE_MONTH = 43200
    LIFE_UNLIMITED = 0

    LIFETIMES = (
        (LIFE_HOUR, '1 Hour'),
        (LIFE_12H, '12 Hours'),
        (LIFE_DAY, '1 Day'),
        (LIFE_WEEK, '1 Week'),
        (LIFE_MONTH, '1 Month'),
        (LIFE_UNLIMITED, 'Unlimited'),
        )

    user = models.ForeignKey(User, editable=False)
    type = models.IntegerField(choices=CHOICES, blank=True)    
    source = models.CharField(max_length=64, blank=True)
    keyword = models.CharField(max_length=64, blank=True)
    tag = models.CharField(max_length=64, blank=True)
    priority = models.IntegerField(choices=Priority.PRIORITY_CHOICES, blank=True)
    lifetime = models.IntegerField(choices=LIFETIMES, blank=True, default=LIFE_UNLIMITED)
    created = models.DateTimeField(auto_now_add=True)
    latest = models.DateTimeField(null=True)
    count = models.IntegerField(default=0)
    active = models.BooleanField(default=True)
    deleted = models.BooleanField(default=False)

    class Meta:
        db_table = "twitter"

