#N&#x014d;tifs Notifier Management

`notif-mgmt` is a Python/Django-based Web application for managing a
user's notifications, authorizations, and rules and methods for user
alerts. It also provides the API for authorizing new notifiers. It
works alongside the
[notif-agent](https://github.com/jimfenton/notif-agent) package, which
runs continuously as a daemon for processing incoming notifications.

This N&#x014d;tifs agent uses the MongoDB database, because a schemaless
database allows arbitrary-sized notifs and has accommodated seamless
changes in the format of notifs during the development process. Since
Django does not natively support MongoDB, this package uses
[django-mongodb-engine](http://django-nonrel.org/), which as the name
suggests is a fork of Django with MongoDB support.

The `notif-management` code has been tested with:

* Python 2.7
* Django 1.5.8 (installed as part of django-mongodb)
* djangotoolbox 1.6.2
* pymongo 2.7.2

##Caveats

Note that the Django version 1.5.x is somewhat behind the
current version, due to compatibility requirements of
`django-mongodb`. This may mean that it is vulnerable to security
issues that have been corrected in later versions.

This software has not yet been extensively tested for security, and
should be treated with caution. In particular, the multitenant
capabilities (multiple users, each with their own notifications,
authorizations, etc.) are thought to be incomplete.

##Installation

It is assumed that you have some familiarity with Django application
structure; if not, please refer to the
[documentation](https://docs.djangoproject.com/en/1.5/). Also refer to the `django-mongodb-engine`
[documentation](https://django-mongodb-engine.readthedocs.org/en/latest/)
for information on installing the required Django fork and supporting
packages.

Note that when running the code in production (with DEBUG turned off
in the configuration file), it is necessary to move the static files
to a separate location, normally hosted directly directly from a web
server such as Apache or nginx. Reder to the Django
[Deployment Checklist](https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/)
for more information on putting the server into production.




