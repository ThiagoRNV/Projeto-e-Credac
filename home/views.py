from django.shortcuts import render # type: ignore
from django.contrib.auth.decorators import login_required

from .models import Permissions
from django.views import View


def home(request):
    return render(request, 'base.html')

   