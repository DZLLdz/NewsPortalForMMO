from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.contrib.auth import login, get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from .models import BaseRegisterForm


class BaseRegisterView(CreateView):
    model = get_user_model()
    form_class = BaseRegisterForm
    success_url = reverse_lazy('registration_complite')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.save()
        user_email = form.cleaned_data.get('email')
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        domain = get_current_site(self.request).domain if not settings.DEBUG else '127.0.0.1:8000'
        subject = 'Activate your account'
        message = render_to_string('sign/activation_email.html', {
            'user': user,
            'domain': domain,
            'uid': uid,
            'token': token,
        })
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user_email])
        return super().form_valid(form)


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = get_user_model().objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect('news_list')
    else:
        return render(request, 'sign/activation_invalid.html')


def registration_complete(request):
    return render(request, 'sign/registration_complete.html')
