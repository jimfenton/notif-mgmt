# N&#x014d;tifs Agent Management

`notif-mgmt` is a Python/Django-based Web application for managing a
user's notifications, authorizations, and rules and methods for user
alerts. It also provides the API for authorizing new notifiers. It
works alongside the
[notif-agent](https://github.com/jimfenton/notif-agent) package, which
runs continuously as a daemon for processing incoming notifications.

This N&#x014d;tifs agent uses the [PostgreSQL](https://www.postgresql.org/)
database. This is a change from earlier versions that had used MongoDB because of the lack of MongoDB support in current, supported versions of Django.

The `notif-mgmt` code uses and has been tested with:

* Python 3.7.3
* Django 3.0.7
* PostgreSQL 11.7
* ZURB [Foundation](https://get.foundation/) 5.5.1

## Caveats

This software has not yet been extensively tested for security, and
should be treated with caution. In particular, the multitenant
capabilities (multiple users, each with their own notifications,
authorizations, etc.) are thought to be incomplete.

## Installation

It is assumed that you have some familiarity with Django application
structure; if not, please refer to the
[documentation](https://docs.djangoproject.com/en/3.0/).

The `notif/settings.py` file will need particular attention. It contains
domain names and the like, but also has site-specific secret values
that have been removed from the version on the repository.

Note that when running the code in production (with DEBUG turned off
in the configuration file), it is necessary to move the static files
to a separate location, normally hosted directly directly from a web
server such as Apache or nginx. Refer to the Django
[Deployment Checklist](https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/)
for more information on putting the server into production.




