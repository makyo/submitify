from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def create_review(request, call_id=None, call_slug=None, submission_id=None):
    call = get_object_or_404(Call, pk=call_id)
    if request.user not in call.readers:
        messages.error(request, 'Only readers for this call may view '
                       'submission reviews')
        return render(request, 'submitify/permission_denied.html', {}, status=403)
    submission = get_object_or_404(Submission, pk=submission_id, call=call)
    if request.user != call.owner:
        review = submission.review_set.get(owner=request.user)
        messages.warning(request, 'Only the call owner may list all reviews')
        return redirect(review.get_absolute_url())
    form = forms.ReviewForm()
    if request.method == 'POST':
        form = forms.ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.owner = request.user
            review.submission = submission
            review.save()
            form.save_m2m()
            return redirect(review.get_absolute_url())
    return render(request, 'submitify/reviews/create.html', {
        'call': call,
        'submission': submission,
        'form': form,
    })



@login_required
def view_review(request, call_id=None, call_slug=None, submission_id=None,
                review_id=None):
    call = get_object_or_404(Call, pk=call_id)
    if request.user not in call.readers:
        messages.error(request, 'Only readers for this call may view '
                       'submission reviews')
        return render(request, 'submitify/permission_denied.html', {}, status=403)
    submission = get_object_or_404(Submission, pk=submission_id, call=call)
    review = get_object_or_404(Review, pk=review_id, submission=submission)
    if request.user not in [review.owner, call.owner]:
        messages.error(request, 'Only readers for this call may view '
                       'submission reviews')
        return render(request, 'submitify/permission_denied.html', {}, status=403)
    return render(request, 'submitify/reviews/view.html', {
        'call': call,
        'submission': submission,
        'review': review,
    })


@login_required
def edit_review(request, call_id=None, call_slug=None, submission_id=None,
                review_id=None):
    review = get_object_or_404(Review, pk=review_id, submission=submission)
    if request.user != review.owner:
        messages.error(request, 'Only the reviewer may edit their review')
        return render(request, 'submitify/permission_denied.html', {}, status=403)
    form = forms.ReviewForm(instance=review)
    if request.method == 'POST':
        form = forms.ReviewForm(request.POST, instance=review)
        if form.is_valid():
            review = form.save()
            return redirect(review.get_absolute_url())
    return render(request, 'submitify/reviews/create.html', {
        'call': call,
        'submission': submission,
        'form': form,
    })
