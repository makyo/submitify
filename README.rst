=========
Submitify
=========

Multi-format submission accepting platform.

Quick start
-----------

1. Add "submitify" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'submitify',
    ]

   Ensure that you have `django.contrib.auth` added as an application as well.

2. Include the submitify URLconf in your project urls.py like this::

    url(r'^submitify/', include('submitify.urls')),

3. Run `python manage.py migrate` to create the submitify models.

4. Start the development server.

5. Visit http://127.0.0.1:8000/submitify/ to participate in the poll.
