from django.urls import path
from validacao.views.outros_modelos.processamento import ProcessamentoServicoView

urlpatterns = [
    path('', ProcessamentoServicoView.as_view(), name='cte_process')
]