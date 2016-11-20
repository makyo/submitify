=========
Submitify
=========

|Build Status| |Coverage Status| |PyPI|

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

3. Run ``python manage.py migrate`` to create the submitify models.

4. Start the development server.

5. Visit http://127.0.0.1:8000/submitify/ to see the app.

Notes for the pluggable application
-----------------------------------

The standalone application is basically ready to use as one would normally run
a Django app, but the pluggable application has a few more things to note.

- Submitify hooks into the Django permissions system.  Creating a new
  call-for-submissions requires the ``submitify.add_call`` permission, so
  publishers should be added to a group with that permission.
- Submitify is designed, loosely, for a site using `Bootstrap
  <https://getbootstrap.com>`__, so elements are classed as such, but this is
  designed to not be a hard requirement.  To that end, some styles are defined within the templates.
- Applications must implement the ability to add users as readers/invite users
  as writers.  A form for doing such is available at
  ``submitify.forms.InviteForm``.  The view should look something like this::

    def view_user(request, username=None):
        user = get_object_or_404(User, username=username)
        ...
        invite_calls_reading = []
        invite_calls_writing = []
        if request.user.is_authenticated and request.user != user:
            invite_calls_reading = request.user.submitify_calls_editing.filter(
                  ~Q(readers__in=[user]),
                status__in=[
                    Call.NOT_OPEN_YET,
                    Call.OPEN
                  ])
            invite_calls_writing = request.user.submitify_calls_reading.filter(
                    status__in=[
                    Call.NOT_OPEN_YET,
                    Call.OPEN,
                  ],
                invite_only=True)
        invite_reader_form = InviteForm(initial={
              'user': user,
          })
        invite_reader_form.fields['calls'].queryset = invite_calls_reading
        invite_writer_form = InviteForm(initial={
              'user': user,
          })
        invite_writer_form.fields['calls'].queryset = invite_calls_writing
        return render(request, 'view_profile.html', {
              ...
              'invite_reader_form': (invite_reader_form if
                                   len(invite_calls_reading) > 0 else None),
              'invite_writer_form': (invite_writer_form if
                                   len(invite_calls_writing) > 0 else None),
          })

  The template should look something like::

    {% if invite_reader_form %}
        <form method="post" action="{% url 'submitify:invite_reader' %}">
            {% csrf_token %}
            {{ invite_reader_form.user }}
            <div class="form-group">
                <label for="id_calls">Invite user as a reader to...</label>
                {{ invite_reader_form.calls }}
            </div>
        </form>
    {% endif %}
    {% if invite_writer_form %}
        <form method="post" action="{% url 'submitify:invite_writer' %}">
            {% csrf_token %}
            {{ invite_writer_form.user }}
            <div class="form-group">
                <label for="id_calls">Invite user as a writer to...</label>
                {{ invite_writer_form.calls }}
            </div>
        </form>
    {% endif %}

  See the standalone application for more information.

Further information
-------------------

Source, issues, and further information:
  `GitHub <https://github.com/OpenFurry/submitify>`__
Author
  `The OpenFurry Contributors <http://OpenFurry.org>`__

.. |Build Status| image:: https://travis-ci.org/OpenFurry/submitify.svg?branch=master
   :target: https://travis-ci.org/OpenFurry/submitify
.. |Coverage Status| image:: https://coveralls.io/repos/github/OpenFurry/submitify/badge.svg?branch=master
   :target: https://coveralls.io/github/OpenFurry/submitify?branch=master
.. |PyPI| image:: https://img.shields.io/pypi/v/django-submitify.svg
   :target: https://pypi.python.org/pypi/django-submitify/
