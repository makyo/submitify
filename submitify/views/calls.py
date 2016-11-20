from django.contrib import messages
from django.contrib.auth.decorators import (
    login_required,
    permission_required,
)
from django.contrib.auth.models import User
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)
from django.views.decorators.http import require_POST

from submitify.forms import (
    CallForm,
    GuidelineFormset,
    InviteForm,
)
from submitify.models import (
    Call,
    Guideline,
    Notification,
)


def list_calls(request):
    subtitle_parts = ['open']
    acceptable_statuses = [Call.OPEN]
    if 'opening-soon' in request.GET:
        acceptable_statuses.append(Call.NOT_OPEN_YET)
        subtitle_parts.append('opening soon')
    if 'closed-reviewing' in request.GET:
        acceptable_statuses.append(Call.CLOSED_REVIEWING)
        subtitle_parts.append('closed (reviewing)')
    if 'closed-completed' in request.GET:
        acceptable_statuses.append(Call.CLOSED_COMPLETED)
        subtitle_parts.append('closed (completed)')
    calls = Call.objects.filter(status__in=acceptable_statuses)
    subtitle = 'Showing calls: {}'.format(', '.join(subtitle_parts))
    return render(request, 'submitify/calls/list.html', {
        'title': 'Calls for submissions',
        'subtitle': subtitle,
        'calls': calls,
    })


def view_call(request, call_id=None, call_slug=None):
    call = get_object_or_404(Call, pk=call_id)
    notifications = Notification.objects.filter(
        call=call, targets__in=[request.user])
    can_submit = True
    if (call.restricted_to.count() > 0 and
            request.user not in call.restricted_to.all()):
        can_submit = False
    elif (not call.readers_can_submit and request.user in call.readers.all()):
        can_submit = False
    return render(request, 'submitify/calls/view.html', {
        'title': call.title,
        'subtitle': call.get_status_display(),
        'call': call,
        'can_submit': can_submit,
        'with_submissions': (request.user in call.readers.all() or
                             request.user == call.owner),
        'notifications': notifications,
    })


@login_required
@permission_required('submitify.add_call')
def create_call(request):
    form = CallForm()
    guideline_set = GuidelineFormset()
    if request.method == 'POST':
        form = CallForm(request.POST)
        guideline_set = GuidelineFormset(request.POST)
        if form.is_valid():
            call = form.save(commit=False)
            call.owner = request.user
            call.save()
            form.save_m2m()
            for guideline_form in guideline_set:
                guideline = guideline_form.save(commit=False)
                guideline.call = call
                guideline.save()
                guideline_form.save_m2m()
            return redirect(call.get_absolute_url())
    return render(request, 'submitify/calls/create.html', {
        'title': 'Create new call for submissions',
        'form': form,
        'guideline_set': guideline_set,
        'guideline_defaults': Guideline.DEFAULT_KEYS,
    })


@login_required
def edit_call(request, call_id=None, call_slug=None):
    call = get_object_or_404(Call, pk=call_id)
    if request.user != call.owner:
        messages.error(request, 'Only the call owner may edit the call')
        return render(request, 'submitify/permission_denied.html', {},
                      status=403)
    form = CallForm(instance=call)
    guideline_set = GuidelineFormset(initial=[g for g in
                                              call.guideline_set.all()])
    if request.method == 'POST':
        form = CallForm(request.POST, instance=call)
        guideline_set = GuidelineFormset(request.POST)
        if form.is_valid():
            call = form.save(commit=False)
            call.save()
            form.save_m2m()
            for guideline in call.guideline_set.all():
                guideline.delete()
            for guideline_form in guideline_set:
                guideline = guideline_form.save(commit=False)
                guideline.call = call
                guideline.save()
                guideline_form.save_m2m()
            return redirect(call.get_absolute_url())
    return render(request, 'submitify/calls/create.html', {
        'title': call.title,
        'subtitle': 'Editing',
        'form': form,
        'guideline_set': guideline_set,
        'guideline_defaults': Guideline.DEFAULT_KEYS
    })


@login_required
@require_POST
def invite_reader(request):
    form = InviteForm(request.POST)
    reader = get_object_or_404(User, pk=int(form.data.get('user')))
    call = get_object_or_404(Call, pk=int(form.data.get('calls')))
    if request.user != call.owner:
        messages.error(request, 'Only the call owner may invite readers')
        return render(request, 'submitify/permission_denied.html', {},
                      status=403)
    call.readers.add(reader)
    return redirect(call.get_absolute_url())


@login_required
def invite_writer(request):
    form = InviteForm(request.POST)
    reader = get_object_or_404(User, pk=int(form.data.get('user')))
    call = get_object_or_404(Call, pk=int(form.data.get('calls')))
    if request.user != call.owner:
        messages.error(request, 'Only the call owner may invite readers')
        return render(request, 'submitify/permission_denied.html', {},
                      status=403)
    if not call.invite_only:
        messages.error(request, 'This call does not accept writer '
                       'invitations')
        return render(request, 'submitify/permission_denied.html', {},
                      status=403)
    call.restricted_to.add(reader)
    return redirect(call.get_absolute_url())


@login_required
def next_step(request, call_id=None, call_slug=None):
    call = get_object_or_404(Call, pk=call_id)
    if request.user != call.owner:
        messages.error(request, 'Only the call owner may edit the call')
        return render(request, 'submitify/permission_denied.html', {},
                      status=403)
    if (call.status + 1 > Call.MAX_STATUS):
        messages.error(request, 'Invalid status provided')
    else:
        call.status += 1
        call.save()
        messages.success(request, 'Status updated')
    return redirect(call.get_absolute_url())
