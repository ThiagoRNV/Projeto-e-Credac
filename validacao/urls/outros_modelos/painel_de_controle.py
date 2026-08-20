from django.urls import path
from validacao.views.outros_modelos.outros_em_andamento import CtesView

urlpatterns = [
    path('outros_modelos_em_andamento/', CtesView.as_view(), name='outros_modelos_em_andamento'),
]