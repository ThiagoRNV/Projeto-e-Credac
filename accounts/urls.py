from django.contrib.auth import views as auth_views
from .views import CustomLoginView  # importe sua função (ajuste o caminho conforme seu projeto)
from django.urls import path

urlpatterns = [
    path('login/', CustomLoginView.as_view(template_name='login.html'), name='login'),
    path('redirect/', CustomLoginView.login_redirect, name='login_redirect'),
]
