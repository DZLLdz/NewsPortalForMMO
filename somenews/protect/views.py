from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render
from newspages.models import Subscription, News, Response
from newspages.tasks import notify_about_react
from .filters import PersonalFilter
from .forms import SubscriptionForm


class IndexView(LoginRequiredMixin, ListView):
    model = Response
    template_name = 'protect/protect_page.html'
    context_object_name = 'responses'

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        queryset = queryset.filter(responseNews__author=user)
        self.filterset = PersonalFilter(self.request.GET, queryset=queryset)

        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['response'] = self.filterset
        context['categories'] = dict(News.TYPENEWS)
        return context


@login_required
def subscribe_to_category(request):
    if request.method == 'POST':
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            category = form.cleaned_data['category']
            try:
                Subscription.objects.create(user=request.user, category=category)
                return redirect('subscriptions_list')
            except IntegrityError:
                form.add_error(None, 'Вы уже подписаны на эту категорию.')
    else:
        form = SubscriptionForm()

    return render(request, 'protect/subscribe.html', {'form': form})


@login_required
def subscriptions_list(request):
    subscriptions = Subscription.objects.filter(user=request.user)
    return render(request, 'protect/subscriptions_list.html', {'subscriptions': subscriptions})


@login_required
def unsubscribe(request, subscription_id):
    subscription = get_object_or_404(Subscription, id=subscription_id, user=request.user)
    if request.method == 'POST':
        subscription.delete()
        return redirect('subscriptions_list')


@login_required
def approve_comment(request, response_id):
    comment = get_object_or_404(Response, id=response_id)
    comment_json = comment.toJSON()
    status_reaction = 'approve'
    if request.user:
        comment.is_approved = True
        notify_about_react(comment_json, comment.responseAuthor.email, comment.responseNews.title, status_reaction)
        comment.save()
        return redirect('personal')
    else:
        return redirect('personal')


@login_required
def reject_comment(request, response_id):
    comment = get_object_or_404(Response, id=response_id)
    status_reaction = 'reject'
    if request.user:
        notify_about_react(comment.toJSON(), comment.responseAuthor.email,
                           comment.responseNews.title, status_reaction)
        comment.delete()
        return redirect('personal')
    else:
        return redirect('personal')


@login_required
def delete_comment(request, response_id):
    comment = get_object_or_404(Response, id=response_id)
    status_reaction = 'delete'
    if request.user:
        if not comment.is_approved:
            notify_about_react(comment.toJSON(), comment.responseAuthor.email,
                               comment.responseNews.title, status_reaction)
        comment.delete()
        return redirect('personal')
    else:
        return redirect('personal')
