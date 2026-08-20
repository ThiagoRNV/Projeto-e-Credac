from typing import Any
from django.contrib import messages

from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.urls import reverse_lazy

class CustomLoginView(LoginView):

    def get_success_url(self):
        access_mode = self.request.POST.get('access_mode')

        if access_mode == 'admin':
            return reverse_lazy('admin:index')
        else:
            return super().get_success_url()

    def login_redirect(request):
        if request.user.is_staff:
            return redirect('/admin/')
        return redirect('home')
