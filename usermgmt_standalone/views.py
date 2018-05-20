from django.contrib.auth import (
    authenticate,
    login,
)
from django.contrib.auth.models import User
from django.urls import reverse
from django.db.models import Q
from django.shortcuts import (
    get_object_or_404,
    render,
)
from django.views.generic import FormView

from .forms import RegisterForm
from submitify.forms import InviteForm
from submitify.models import Call


class Register(FormView):
    """View to register a new user."""
    template_name = 'registration/new.html'
    form_class = RegisterForm

    def form_valid(self, form):
        form.save()
        new_user = authenticate(username=form.cleaned_data['username'],
                                password=form.cleaned_data['password1'])
        login(self.request, new_user)
        return super(Register, self).form_valid(form)

    def get_success_url(self):
        return self.request.POST.get(
            'next', self.request.GET.get(
                'next', reverse('usermgmt_standalone:view_user', kwargs={
                    'username': self.request.user.username,
                })))

    def get_context_data(self, **kwargs):
        context = super(Register, self).get_context_data(**kwargs)
        context['title'] = 'Register'
        return context


def view_user(request, username=None):
    user = get_object_or_404(User, username=username)
    acceptable_statuses = [
        Call.NOT_OPEN_YET,
        Call.OPEN,
    ]
    if 'closed-reviewing' in request.GET:
        acceptable_statuses.append(Call.CLOSED_REVIEWING)
    if 'closed-completed' in request.GET:
        acceptable_statuses.append(Call.CLOSED_COMPLETED)
    calls_running = user.submitify_calls_editing.filter(
        status__in=acceptable_statuses)
    calls_reading = Call.objects.filter(readers__in=[user],
                                        status__in=acceptable_statuses)
    calls_submitting = Call.objects.filter(
        id__in=[s.call.id for s in user.submitify_submissions.all()],
        status__in=acceptable_statuses)
    invite_calls_reading = []
    invite_calls_writing = []
    if request.user.is_authenticated and request.user != user:
        invite_calls_reading = request.user.submitify_calls_editing.filter(
            ~Q(readers__in=[user]),
            status__in=[
                Call.NOT_OPEN_YET,
                Call.OPEN
            ])
        invite_calls_writing = request.user.submitify_calls_editing.filter(
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
        'title': user.username,
        'profile': user,
        'calls_running': calls_running,
        'calls_reading': calls_reading,
        'calls_submitting': calls_submitting,
        'invite_reader_form': (invite_reader_form if
                               len(invite_calls_reading) > 0 else None),
        'invite_writer_form': (invite_writer_form if
                               len(invite_calls_writing) > 0 else None),
    })
