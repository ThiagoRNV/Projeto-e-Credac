from django.urls import path
from validacao.views.outros_modelos.processamento import ProcessamentoOutrosModelos

urlpatterns = [
    path('', ProcessamentoOutrosModelos.as_view(), name='cte_process')
]